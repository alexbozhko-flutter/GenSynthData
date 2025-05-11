#!/usr/bin/env python3
"""
Data preparation and anonymization script.
Exports and anonymizes data from the database.
"""

import pandas as pd
from sqlalchemy import create_engine, text
from faker import Faker
import configparser
from pathlib import Path
import random
import logging
from datetime import datetime

def setup_logging():
    """Setup logging configuration."""
    log_dir = Path(__file__).parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f'data_preparation_{timestamp}.log'
    
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

def load_product_types():
    """Load multilingual product types from file."""
    logger = logging.getLogger(__name__)
    product_list_path = Path(__file__).parent.parent / 'data' / 'anonymized' / 'productList.txt'
    
    if not product_list_path.exists():
        logger.error(f"Product list file not found at {product_list_path}")
        raise FileNotFoundError(f"Product list file not found at {product_list_path}")
    
    product_data = []
    invalid_lines = []
    total_lines = 0
    
    logger.info(f"Starting to read product list from {product_list_path}")
    
    with open(product_list_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            total_lines += 1
            line = line.strip()
            if line and not line.startswith('*'):
                parts = line.split('::')
                if len(parts) >= 5:
                    product = {
                        'base_name': parts[0].strip(),
                        'base_name_fr': parts[1].strip(),
                        'base_name_de': parts[2].strip(),
                        'base_name_it': parts[3].strip(),
                        'base_name_uk': parts[4].strip() if len(parts) > 4 else ''
                    }
                    
                    # Проверка на пустые значения
                    empty_fields = [k for k, v in product.items() if not v]
                    if empty_fields:
                        logger.warning(f"Line {line_num}: Empty fields found: {', '.join(empty_fields)}")
                        invalid_lines.append(line_num)
                        continue
                    
                    logger.debug(f"Line {line_num}: Successfully parsed product names")
                    product_data.append(product)
                else:
                    logger.warning(f"Line {line_num}: Invalid format - expected 5 parts, got {len(parts)}")
                    invalid_lines.append(line_num)
    
    logger.info(f"Finished reading product list:")
    logger.info(f"- Total lines processed: {total_lines}")
    logger.info(f"- Valid products found: {len(product_data)}")
    logger.info(f"- Invalid lines: {len(invalid_lines)}")
    if invalid_lines:
        logger.info(f"- Invalid line numbers: {invalid_lines}")
    
    return product_data

def verify_table_columns(connection):
    """Проверяем наличие всех необходимых колонок в таблице."""
    try:
        result = connection.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'producttypes'
        """))
        columns = [row[0] for row in result.fetchall()]
        required_columns = ['base_name', 'base_name_fr', 'base_name_de', 'base_name_it', 'base_name_uk']
        
        # Проверяем каждую требуемую колонку
        for col in required_columns:
            if col not in columns:
                # Если колонки нет, создаем её
                print(f"Adding missing column: {col}")
                connection.execute(text(f"ALTER TABLE producttypes ADD COLUMN {col} TEXT"))
        
        print("All required columns are present in the table")
        
    except Exception as e:
        print(f"Error verifying table columns: {str(e)}")
        raise

def update_product_types(connection, product_data):
    """Update multilingual names in producttypes table."""
    logger = logging.getLogger(__name__)
    try:
        logger.info("Starting product types update process")
        
        # Проверяем и создаем отсутствующие колонки
        verify_table_columns(connection)
        
        # Получаем все существующие записи из таблицы
        result = connection.execute(text("SELECT id, base_name FROM producttypes"))
        existing_records = {row[0]: row[1] for row in result.fetchall()}
        total_records = len(existing_records)
        logger.info(f"Total records in producttypes table: {total_records}")
        
        # Статистика обновления
        stats = {
            'total': total_records,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }
        
        if len(product_data) < total_records:
            logger.warning(
                f"Product data ({len(product_data)} items) is less than total records "
                f"({total_records}). Will use random values with repetition."
            )
            product_data = product_data * (total_records // len(product_data) + 1)
        
        random.shuffle(product_data)
        logger.info("Starting records update...")
        
        for record_id, base_name in existing_records.items():
            try:
                # Берем случайный набор переводов из product_data
                translations = product_data[record_id % len(product_data)]
                
                connection.execute(
                    text("""
                        UPDATE producttypes 
                        SET base_name_fr = :base_name_fr,
                            base_name_de = :base_name_de,
                            base_name_it = :base_name_it,
                            base_name_uk = :base_name_uk
                        WHERE id = :id
                    """),
                    {
                        "base_name_fr": translations['base_name_fr'],
                        "base_name_de": translations['base_name_de'],
                        "base_name_it": translations['base_name_it'],
                        "base_name_uk": translations['base_name_uk'],
                        "id": record_id
                    }
                )
                stats['updated'] += 1
                
                if stats['updated'] % 50 == 0:
                    logger.info(f"Progress: {stats['updated']}/{total_records} records updated ({(stats['updated']/total_records*100):.1f}%)")
                
                # Логируем первые несколько обновлений для проверки
                if stats['updated'] <= 5:
                    logger.info(f"\nExample update (record {record_id}):")
                    logger.info(f"Original base_name: {base_name}")
                    logger.info(f"Added translations:")
                    logger.info(f"- French:    {translations['base_name_fr']}")
                    logger.info(f"- German:    {translations['base_name_de']}")
                    logger.info(f"- Italian:   {translations['base_name_it']}")
                    logger.info(f"- Ukrainian: {translations['base_name_uk']}")
                
            except Exception as e:
                logger.error(f"Error updating record {record_id}: {str(e)}")
                stats['errors'] += 1
                continue
        
        # Финальная статистика
        logger.info("\nUpdate completed. Statistics:")
        logger.info(f"- Total records processed: {stats['total']}")
        logger.info(f"- Successfully updated: {stats['updated']}")
        logger.info(f"- Skipped: {stats['skipped']}")
        logger.info(f"- Errors: {stats['errors']}")
        
        # Проверка результатов
        logger.info("\nVerifying updates...")
        result = connection.execute(text("""
            SELECT COUNT(*) 
            FROM producttypes 
            WHERE base_name IS NOT NULL 
              AND base_name_fr IS NOT NULL 
              AND base_name_de IS NOT NULL 
              AND base_name_it IS NOT NULL 
              AND base_name_uk IS NOT NULL
        """))
        complete_records = result.fetchone()[0]
        logger.info(f"Records with all languages filled: {complete_records}/{total_records}")
        
    except Exception as e:
        logger.error(f"Error in update_product_types: {str(e)}")
        raise

def main():
    """Main function for data preparation."""
    logger = setup_logging()
    logger.info("Starting data preparation process")
    
    try:
        engine = get_db_connection()
        logger.info("Database connection established")
        
        with engine.begin() as connection:
            result = connection.execute(text("SELECT version();"))
            logger.info(f"Connected to PostgreSQL: {result.fetchone()}")
            
            product_data = load_product_types()
            logger.info(f"Loaded {len(product_data)} multilingual product types")
            
            update_product_types(connection, product_data)
            
        logger.info("Data preparation process completed successfully")
        
    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}")
        raise
    
if __name__ == "__main__":
    main() 