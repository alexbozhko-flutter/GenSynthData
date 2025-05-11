#!/usr/bin/env python3
"""
Script for exporting product type IDs and names from the database.
Saves data to a text file with '::' as delimiter.
"""

from sqlalchemy import create_engine, text
import configparser
from pathlib import Path
import logging
from datetime import datetime

def setup_logging():
    """Setup logging configuration."""
    log_dir = Path(__file__).parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f'get_producttype_names_{timestamp}.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def get_db_connection():
    """Create database connection from config file."""
    config = configparser.ConfigParser()
    config_path = Path(__file__).parent.parent / 'config' / 'database.ini'
    
    if not config_path.exists():
        raise FileNotFoundError(
            f"Database configuration file not found at {config_path}. "
            "Please copy database.ini.example to database.ini and update with your credentials."
        )
    
    config.read(config_path)
    
    if 'postgresql' not in config:
        raise KeyError("PostgreSQL configuration section not found in config file")
    
    db_params = config['postgresql']
    
    connection_string = (
        f"postgresql+psycopg2://{db_params['user']}:{db_params['password']}"
        f"@{db_params['host']}:{db_params['port']}/{db_params['database']}"
    )
    return create_engine(connection_string)

def export_product_types(connection, output_file):
    """Export product type IDs and names to a text file."""
    logger = logging.getLogger(__name__)
    try:
        # Получаем все записи из таблицы
        result = connection.execute(text("SELECT id, name FROM producttypes ORDER BY id"))
        records = result.fetchall()
        
        logger.info(f"Found {len(records)} records to export")
        
        # Создаем директорию для файла, если её нет
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Записываем данные в файл
        with open(output_file, 'w', encoding='utf-8') as f:
            for record in records:
                f.write(f"{record[0]}::{record[1]}\n")
        
        logger.info(f"Successfully exported data to {output_file}")
        logger.info("First 5 exported records:")
        
        # Показываем первые 5 записей для проверки
        with open(output_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i < 5:
                    logger.info(line.strip())
                else:
                    break
                    
    except Exception as e:
        logger.error(f"Error exporting product types: {str(e)}")
        raise

def main():
    """Main function for exporting product types."""
    logger = setup_logging()
    logger.info("Starting product types export process")
    
    try:
        engine = get_db_connection()
        logger.info("Database connection established")
        
        # Определяем путь для выходного файла
        output_file = Path(__file__).parent.parent / 'data' / 'product_types.txt'
        
        with engine.begin() as connection:
            result = connection.execute(text("SELECT version();"))
            logger.info(f"Connected to PostgreSQL: {result.fetchone()}")
            
            export_product_types(connection, output_file)
            
        logger.info("Export process completed successfully")
        
    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main() 