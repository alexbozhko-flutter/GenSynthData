#!/usr/bin/env python3
"""
Script for extracting unique attribute names from product_types_separated.txt
and inserting them into product_attributes table.
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
    log_file = log_dir / f'extract_product_attributes_{timestamp}.log'
    
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

def extract_attribute_names():
    """Extract unique attribute names from the file."""
    logger = logging.getLogger(__name__)
    input_file = Path(__file__).parent.parent / 'data' / 'product_types_separated.txt'
    
    if not input_file.exists():
        logger.error(f"Input file not found: {input_file}")
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    attribute_names = set()
    total_lines = 0
    
    logger.info(f"Starting to extract attribute names from {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            total_lines += 1
            line = line.strip()
            if line:
                parts = line.split('::')
                # Начинаем с индекса 2, так как 0 - это код, 1 - категория
                for i in range(2, len(parts), 2):
                    if i + 1 < len(parts):  # Проверяем, что есть пара "название-значение"
                        attribute_name = parts[i].strip()
                        if attribute_name:
                            attribute_names.add(attribute_name)
    
    logger.info(f"Finished extracting attribute names:")
    logger.info(f"- Total lines processed: {total_lines}")
    logger.info(f"- Unique attribute names found: {len(attribute_names)}")
    
    return sorted(list(attribute_names))

def insert_attribute_names(connection, attribute_names):
    """Insert unique attribute names into the database."""
    logger = logging.getLogger(__name__)
    try:
        logger.info("Starting attribute names insertion process")
        
        # Статистика вставки
        stats = {
            'total': len(attribute_names),
            'inserted': 0,
            'skipped': 0,
            'errors': 0
        }
        
        # Вставляем названия атрибутов
        for attribute_name in attribute_names:
            try:
                # Проверяем, существует ли уже такой атрибут
                result = connection.execute(
                    text("""
                        SELECT id FROM product_attributes 
                        WHERE attribute_name = :name
                    """),
                    {"name": attribute_name}
                )
                
                if result.fetchone() is None:
                    # Если атрибут не существует, вставляем его
                    connection.execute(
                        text("""
                            INSERT INTO product_attributes (attribute_name)
                            VALUES (:name)
                        """),
                        {"name": attribute_name}
                    )
                    stats['inserted'] += 1
                    if stats['inserted'] <= 5:  # Показываем первые 5 вставок
                        logger.info(f"Inserted attribute: {attribute_name}")
                else:
                    stats['skipped'] += 1
                    logger.debug(f"Attribute already exists: {attribute_name}")
                
                if stats['inserted'] % 100 == 0:
                    logger.info(f"Progress: {stats['inserted']}/{stats['total']} attributes inserted ({(stats['inserted']/stats['total']*100):.1f}%)")
                
            except Exception as e:
                logger.error(f"Error inserting attribute {attribute_name}: {str(e)}")
                stats['errors'] += 1
                continue
        
        # Финальная статистика
        logger.info("\nInsertion completed. Statistics:")
        logger.info(f"- Total attributes to process: {stats['total']}")
        logger.info(f"- Successfully inserted: {stats['inserted']}")
        logger.info(f"- Skipped (already exist): {stats['skipped']}")
        logger.info(f"- Errors: {stats['errors']}")
        
        # Проверка результатов
        logger.info("\nVerifying results...")
        result = connection.execute(text("""
            SELECT COUNT(*) 
            FROM product_attributes
        """))
        total_attributes = result.fetchone()[0]
        logger.info(f"Total attributes in database: {total_attributes}")
        
    except Exception as e:
        logger.error(f"Error in insert_attribute_names: {str(e)}")
        raise

def main():
    """Main function for extracting and inserting attribute names."""
    logger = setup_logging()
    logger.info("Starting attribute names extraction and insertion process")
    
    try:
        engine = get_db_connection()
        logger.info("Database connection established")
        
        with engine.begin() as connection:
            result = connection.execute(text("SELECT version();"))
            logger.info(f"Connected to PostgreSQL: {result.fetchone()}")
            
            attribute_names = extract_attribute_names()
            logger.info(f"Extracted {len(attribute_names)} unique attribute names")
            
            insert_attribute_names(connection, attribute_names)
            
        logger.info("Process completed successfully")
        
    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main() 