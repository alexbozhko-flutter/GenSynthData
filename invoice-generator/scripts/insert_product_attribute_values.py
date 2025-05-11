#!/usr/bin/env python3
"""
Script for inserting product attribute values into product_attribute_values table.
Reads product types and their attributes from product_types_separated.txt file,
finds corresponding products and attributes in the database,
and creates attribute value records.
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
    log_file = log_dir / f'insert_product_attribute_values_{timestamp}.log'
    
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

def get_attribute_id_map(connection):
    """Get mapping of attribute names to their IDs."""
    logger = logging.getLogger(__name__)
    logger.info("Loading attribute name to ID mapping...")
    
    result = connection.execute(text("""
        SELECT id, attribute_name 
        FROM product_attributes
    """))
    
    attribute_map = {row[1]: row[0] for row in result}
    logger.info(f"Loaded {len(attribute_map)} attribute mappings")
    return attribute_map

def process_product_types(connection):
    """Process product types and their attributes from the file."""
    logger = logging.getLogger(__name__)
    input_file = Path(__file__).parent.parent / 'data' / 'product_types_separated.txt'
    
    if not input_file.exists():
        logger.error(f"Input file not found: {input_file}")
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    # Загружаем маппинг атрибутов
    attribute_map = get_attribute_id_map(connection)
    
    # Статистика обработки
    stats = {
        'total_lines': 0,
        'products_found': 0,
        'attributes_inserted': 0,
        'errors': 0
    }
    
    logger.info(f"Starting to process product types from {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            stats['total_lines'] += 1
            line = line.strip()
            if not line:
                continue
            
            try:
                parts = line.split('::')
                if len(parts) < 3:  # Минимум код, категория и одна пара атрибут-значение
                    logger.warning(f"Line {line_num}: Invalid format - not enough parts")
                    continue
                
                product_type_id = int(parts[0])
                
                # Находим все продукты с данным product_type_id
                result = connection.execute(
                    text("""
                        SELECT id 
                        FROM products 
                        WHERE product_type_id = :type_id
                    """),
                    {"type_id": product_type_id}
                )
                
                product_ids = [row[0] for row in result]
                if not product_ids:
                    logger.debug(f"Line {line_num}: No products found for type_id {product_type_id}")
                    continue
                
                stats['products_found'] += len(product_ids)
                
                # Обрабатываем пары атрибут-значение
                for i in range(2, len(parts), 2):
                    if i + 1 >= len(parts):
                        break
                    
                    attribute_name = parts[i].strip()
                    attribute_value = parts[i + 1].strip()
                    
                    if not attribute_name or not attribute_value:
                        continue
                    
                    # Получаем ID атрибута
                    attribute_id = attribute_map.get(attribute_name)
                    if not attribute_id:
                        logger.warning(f"Line {line_num}: Attribute not found in database: {attribute_name}")
                        continue
                    
                    # Вставляем значения атрибутов для каждого продукта
                    for product_id in product_ids:
                        try:
                            connection.execute(
                                text("""
                                    INSERT INTO product_attribute_values 
                                    (product_id, attribute_id, value)
                                    VALUES (:product_id, :attribute_id, :value)
                                """),
                                {
                                    "product_id": product_id,
                                    "attribute_id": attribute_id,
                                    "value": attribute_value
                                }
                            )
                            stats['attributes_inserted'] += 1
                            
                        except Exception as e:
                            logger.error(f"Error inserting attribute value for product {product_id}, "
                                       f"attribute {attribute_name}: {str(e)}")
                            stats['errors'] += 1
                            continue
                
                if line_num % 100 == 0:
                    logger.info(f"Progress: {line_num} lines processed")
                    logger.info(f"- Products found: {stats['products_found']}")
                    logger.info(f"- Attributes inserted: {stats['attributes_inserted']}")
                    logger.info(f"- Errors: {stats['errors']}")
                
            except ValueError as e:
                logger.error(f"Line {line_num}: Invalid product type ID format: {str(e)}")
                stats['errors'] += 1
                continue
            except Exception as e:
                logger.error(f"Line {line_num}: Unexpected error: {str(e)}")
                stats['errors'] += 1
                continue
    
    # Финальная статистика
    logger.info("\nProcessing completed. Statistics:")
    logger.info(f"- Total lines processed: {stats['total_lines']}")
    logger.info(f"- Products found: {stats['products_found']}")
    logger.info(f"- Attributes inserted: {stats['attributes_inserted']}")
    logger.info(f"- Errors: {stats['errors']}")
    
    # Проверка результатов
    logger.info("\nVerifying results...")
    result = connection.execute(text("""
        SELECT COUNT(*) 
        FROM product_attribute_values
    """))
    total_values = result.fetchone()[0]
    logger.info(f"Total attribute values in database: {total_values}")

def main():
    """Main function for processing product types and inserting attribute values."""
    logger = setup_logging()
    logger.info("Starting product attribute values insertion process")
    
    try:
        engine = get_db_connection()
        logger.info("Database connection established")
        
        with engine.begin() as connection:
            result = connection.execute(text("SELECT version();"))
            logger.info(f"Connected to PostgreSQL: {result.fetchone()}")
            
            process_product_types(connection)
            
        logger.info("Process completed successfully")
        
    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main() 