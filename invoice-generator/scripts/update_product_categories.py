#!/usr/bin/env python3
"""
Script for updating product categories in the database.
Reads categories from product_types_separated file and updates base_name field in producttypes table.
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
    log_file = log_dir / f'update_product_categories_{timestamp}.log'
    
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

def load_categories():
    """Load product categories from file."""
    logger = logging.getLogger(__name__)
    input_file = Path(__file__).parent.parent / 'data' / 'product_types_separated.txt'
    
    if not input_file.exists():
        logger.error(f"Input file not found: {input_file}")
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    categories = {}
    invalid_lines = []
    total_lines = 0
    
    logger.info(f"Starting to read categories from {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            total_lines += 1
            line = line.strip()
            if line:
                parts = line.split('::')
                if len(parts) >= 2:  # Минимум код и категория
                    try:
                        code = int(parts[0])
                        category = parts[1]
                        categories[code] = category
                        logger.debug(f"Line {line_num}: Loaded category {category} for code {code}")
                    except ValueError:
                        logger.warning(f"Line {line_num}: Invalid code format - {parts[0]}")
                        invalid_lines.append(line_num)
                else:
                    logger.warning(f"Line {line_num}: Invalid format - expected at least 2 parts, got {len(parts)}")
                    invalid_lines.append(line_num)
    
    logger.info(f"Finished reading categories:")
    logger.info(f"- Total lines processed: {total_lines}")
    logger.info(f"- Valid categories found: {len(categories)}")
    logger.info(f"- Invalid lines: {len(invalid_lines)}")
    if invalid_lines:
        logger.info(f"- Invalid line numbers: {invalid_lines}")
    
    return categories

def update_categories(connection, categories):
    """Update product categories in the database."""
    logger = logging.getLogger(__name__)
    try:
        logger.info("Starting categories update process")
        
        # Статистика обновления
        stats = {
            'total': len(categories),
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }
        
        # Обновляем категории
        for code, category in categories.items():
            try:
                result = connection.execute(
                    text("""
                        UPDATE producttypes 
                        SET base_name = :category
                        WHERE id = :code
                        RETURNING id, base_name
                    """),
                    {
                        "category": category,
                        "code": code
                    }
                )
                
                updated_row = result.fetchone()
                if updated_row:
                    stats['updated'] += 1
                    if stats['updated'] <= 5:  # Показываем первые 5 обновлений
                        logger.info(f"Updated record {code}: {updated_row[1]}")
                else:
                    stats['skipped'] += 1
                    logger.warning(f"No record found with id {code}")
                
                if stats['updated'] % 100 == 0:
                    logger.info(f"Progress: {stats['updated']}/{stats['total']} records updated ({(stats['updated']/stats['total']*100):.1f}%)")
                
            except Exception as e:
                logger.error(f"Error updating record {code}: {str(e)}")
                stats['errors'] += 1
                continue
        
        # Финальная статистика
        logger.info("\nUpdate completed. Statistics:")
        logger.info(f"- Total categories to process: {stats['total']}")
        logger.info(f"- Successfully updated: {stats['updated']}")
        logger.info(f"- Skipped (not found): {stats['skipped']}")
        logger.info(f"- Errors: {stats['errors']}")
        
        # Проверка результатов
        logger.info("\nVerifying updates...")
        result = connection.execute(text("""
            SELECT COUNT(*) 
            FROM producttypes 
            WHERE base_name IS NOT NULL
        """))
        updated_records = result.fetchone()[0]
        logger.info(f"Records with non-null base_name: {updated_records}")
        
    except Exception as e:
        logger.error(f"Error in update_categories: {str(e)}")
        raise

def main():
    """Main function for updating product categories."""
    logger = setup_logging()
    logger.info("Starting product categories update process")
    
    try:
        engine = get_db_connection()
        logger.info("Database connection established")
        
        with engine.begin() as connection:
            result = connection.execute(text("SELECT version();"))
            logger.info(f"Connected to PostgreSQL: {result.fetchone()}")
            
            categories = load_categories()
            logger.info(f"Loaded {len(categories)} categories from file")
            
            update_categories(connection, categories)
            
        logger.info("Update process completed successfully")
        
    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main() 