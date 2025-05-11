#!/usr/bin/env python3
"""
Script for updating product_type_id values in products table.
Replaces values > 400 with random valid values from producttypes table.
"""

import pandas as pd
from sqlalchemy import create_engine, text
import configparser
from pathlib import Path
import random

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

def get_valid_type_ids(connection):
    """Get list of valid product type IDs from producttypes table."""
    result = connection.execute(text("SELECT id FROM producttypes WHERE id <= 400"))
    return [row[0] for row in result.fetchall()]

def update_product_types(connection, valid_type_ids):
    """Update product_type_id values greater than 400 with random valid values."""
    try:
        # Получаем количество записей для обновления
        result = connection.execute(
            text("SELECT COUNT(*) FROM products WHERE product_type_id = 54")
        )
        records_to_update = result.fetchone()[0]
        
        if records_to_update == 0:
            print("No records need to be updated")
            return
        
        print(f"Found {records_to_update} records to update")
        
        # Получаем ID записей, которые нужно обновить
        result = connection.execute(
            text("SELECT id FROM products WHERE product_type_id = 54")
        )
        products_to_update = [row[0] for row in result.fetchall()]
        
        # Обновляем каждую запись случайным значением
        updated_count = 0
        for product_id in products_to_update:
            new_type_id = random.choice(valid_type_ids)
            connection.execute(
                text("UPDATE products SET product_type_id = :new_type_id WHERE id = :product_id"),
                {"new_type_id": new_type_id, "product_id": product_id}
            )
            updated_count += 1
            if updated_count % 100 == 0:
                print(f"Updated {updated_count} records...")
        
        print(f"Successfully updated {records_to_update} records in products table")
        
    except Exception as e:
        print(f"Error updating product types: {str(e)}")
        raise

def main():
    """Main function for updating product types."""
    try:
        # Initialize database connection
        engine = get_db_connection()
        
        # Используем with для автоматического управления транзакцией
        with engine.begin() as connection:
            # Get valid product type IDs
            valid_type_ids = get_valid_type_ids(connection)
            print(f"Found {len(valid_type_ids)} valid product type IDs")
            
            if not valid_type_ids:
                raise ValueError("No valid product type IDs found")
            
            # Update product types
            update_product_types(connection, valid_type_ids)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    main() 