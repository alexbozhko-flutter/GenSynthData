import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from templates.invoice.feiler.generator import FeilerInvoiceGenerator

def generate_test_invoice():
    # Тестовые данные для инвойса
    invoice_data = {
        'recipient_name': 'ООО "Домашний Текстиль"',
        'recipient_street': 'ул. Текстильщиков, 123',
        'recipient_postal_code': '123456',
        'recipient_city': 'МОСКВА',
        'recipient_country': 'РОССИЯ',
        'invoice_date': datetime.now(),
        'customer_number': '12345',
        'invoice_number': 'TEST-001',
        'seller': 'Emanuel Baur Asien/Drittland',
        'contact': 'Anja König',
        'agent': '49112',
        'order': '2069354',
        'items': [
            {
                'item_position': 1,
                'lines': [
                    {
                        'is_bold': True,
                        'content': {
                            'collection': 'ELEGANCE',
                            'product_type': 'ПОЛОТЕНЦЕ',
                            'size': '30x50',
                            'color_id': '317',
                            'quantity': '100 pcs',
                            'price': '12,50'
                        }
                    },
                    {
                        'is_bold': False,
                        'content': {
                            'prefix': 'Article No.:',
                            'value': 'FT-123456',
                            'color': 'Морская волна'
                        }
                    },
                    {
                        'is_bold': False,
                        'content': {
                            'prefix': 'HS-Code',
                            'value': '63029100 Chenille towels, 100% cotton, premium quality'
                        }
                    }
                ],
                'amount': '1250,00'
            },
            {
                'item_position': 2,
                'lines': [
                    {
                        'is_bold': True,
                        'content': {
                            'collection': 'CLASSIC',
                            'product_type': 'ХАЛАТ',
                            'size': 'L',
                            'color_id': '124',
                            'quantity': '50 pcs',
                            'price': '45,00'
                        }
                    },
                    {
                        'is_bold': False,
                        'content': {
                            'prefix': 'Article No.:',
                            'value': 'BR-789012',
                            'color': 'Бордовый'
                        }
                    },
                    {
                        'is_bold': False,
                        'content': {
                            'prefix': 'HS-Code',
                            'value': '61021000 Bathrobes, premium cotton blend'
                        }
                    }
                ],
                'amount': '2250,00'
            }
        ],
        'correspondence_number': '09-2024',
        'correspondence_date': datetime.now(),
        'correspondence_person': 'Татьяна Иванова',
        'delivery_note_number': '4059965',
        'delivery_date': datetime.now()
    }

    # Создаем генератор
    generator = FeilerInvoiceGenerator()
    
    # Определяем пути для выходных файлов
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    output_html = os.path.join(output_dir, 'test_invoice.html')
    output_pdf = os.path.join(output_dir, 'test_invoice.pdf')
    
    # Генерируем инвойс
    html_path, pdf_path = generator.generate(invoice_data, output_html, output_pdf)
    
    print(f"\nТестовый инвойс успешно сгенерирован:")
    print(f"HTML: {html_path}")
    print(f"PDF: {pdf_path}")
    
    return html_path, pdf_path

if __name__ == '__main__':
    generate_test_invoice() 