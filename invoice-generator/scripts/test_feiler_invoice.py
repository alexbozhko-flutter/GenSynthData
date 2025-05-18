from datetime import datetime
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from templates.invoice.feiler.generator import FeilerInvoiceGenerator
from generate_test_data import generate_test_data

def test_feiler_invoice():
    # Генерация тестовых данных с 50 записями
    test_data = generate_test_data(50)
    print(f"\nГенерация инвойса с {len(test_data['items'])} записями")
    
    # Создание генератора
    generator = FeilerInvoiceGenerator()
    
    # Пути для выходных файлов
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    output_html = os.path.join(output_dir, 'test_feiler_invoice.html')
    output_pdf = os.path.join(output_dir, 'test_feiler_invoice.pdf')
    
    # Генерация инвойса
    html_path, pdf_path = generator.generate(test_data, output_html, output_pdf)
    
    print(f"\nСгенерированные файлы:")
    print(f"HTML: {html_path}")
    print(f"PDF: {pdf_path}")
    
    # Вывод информации о записях
    print("\nПример первых 5 записей из инвойса:")
    for item in test_data['items'][:5]:
        print(f"{item['item_position']}. {item['product_design']} - "
              f"{item['parameters']['size']} - {item['parameters']['color']} - "
              f"{item['quantity']} шт. x {item['purchase_price']} = {item['item_amount']}")

if __name__ == '__main__':
    test_feiler_invoice() 