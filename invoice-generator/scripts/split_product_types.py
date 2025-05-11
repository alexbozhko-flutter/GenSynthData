#!/usr/bin/env python3
"""
Script for splitting product_types.txt into four equal parts.
"""

from pathlib import Path
import logging
from datetime import datetime
import math

def setup_logging():
    """Setup logging configuration."""
    log_dir = Path(__file__).parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f'split_product_types_{timestamp}.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def split_file(input_file, output_dir):
    """Split input file into four equal parts."""
    logger = logging.getLogger(__name__)
    
    try:
        # Создаем директорию для выходных файлов
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Читаем все строки из файла
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        logger.info(f"Total lines in input file: {total_lines}")
        
        # Вычисляем размер каждой части
        part_size = math.ceil(total_lines / 4)
        logger.info(f"Lines per part: {part_size}")
        
        # Разбиваем файл на части
        for i in range(4):
            start_idx = i * part_size
            end_idx = min((i + 1) * part_size, total_lines)
            
            output_file = output_dir / f'product_types_part_{i+1}.txt'
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.writelines(lines[start_idx:end_idx])
            
            logger.info(f"Created part {i+1}: {output_file}")
            logger.info(f"Lines in part {i+1}: {end_idx - start_idx}")
            
            # Показываем первые 3 строки каждой части для проверки
            logger.info(f"First 3 lines of part {i+1}:")
            for line in lines[start_idx:start_idx + 3]:
                logger.info(line.strip())
            logger.info("-" * 50)
        
        logger.info("File splitting completed successfully")
        
    except Exception as e:
        logger.error(f"Error splitting file: {str(e)}")
        raise

def main():
    """Main function for splitting product types file."""
    logger = setup_logging()
    logger.info("Starting file splitting process")
    
    try:
        # Определяем пути к файлам
        input_file = Path(__file__).parent.parent / 'data' / 'product_types.txt'
        output_dir = Path(__file__).parent.parent / 'data' / 'split'
        
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        split_file(input_file, output_dir)
        
    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main() 