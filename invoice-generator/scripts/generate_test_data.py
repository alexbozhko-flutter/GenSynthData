from datetime import datetime
import random

def generate_test_data(num_records=50):
    """Генерирует тестовые данные для инвойса с указанным количеством записей."""
    
    # Базовые продукты
    products = [
        {
            'design': 'BELLE FLEUR',
            'article_prefix': 'belle146',
            'sizes': ['50/100', '75/150', '37/50', '150/200'],
            'colors': ['147 pebble', '227 breeze', '445 stone', '666 black']
        },
        {
            'design': 'SUMMER DAY',
            'article_prefix': 'sumday032',
            'sizes': ['50/100', '75/150', '150/100', '200/200'],
            'colors': ['', '147 white', '227 blue', '445 beige']
        },
        {
            'design': 'FLOWER MEADOW',
            'article_prefix': 'flowermea012',
            'sizes': ['50/100', '75/150', '37/50', '150/200'],
            'colors': ['227 breeze', '445 stone', '666 black', '777 green']
        },
        {
            'design': 'WINTER DREAMS',
            'article_prefix': 'wintdre064',
            'sizes': ['50/100', '75/150', '37/50', '150/200'],
            'colors': ['147 snow', '227 ice', '445 frost', '666 night']
        },
        {
            'design': 'AUTUMN LEAVES',
            'article_prefix': 'autmlev088',
            'sizes': ['50/100', '75/150', '37/50', '150/200'],
            'colors': ['147 gold', '227 red', '445 brown', '666 orange']
        }
    ]
    
    # Генерация записей
    items = []
    for i in range(num_records):
        product = random.choice(products)
        size = random.choice(product['sizes'])
        color = random.choice(product['colors'])
        
        # Генерация артикула
        size_code = '0001' if size == '50/100' else '0002' if size == '37/50' else '0005' if size == '75/150' else '0006'
        color_code = '0000' if not color else color.split()[0]
        article_no = f"{product['article_prefix']}.{size_code}.{color_code}"
        
        # Генерация цены в зависимости от размера
        base_price = 20.30 if size == '50/100' else 9.60 if size == '37/50' else 43.00 if size == '75/150' else 56.80
        quantity = random.randint(1, 5)
        
        items.append({
            'item_position': i + 1,
            'product_design': product['design'],
            'article_no': article_no,
            'parameters': {
                'size': size,
                'color': color
            },
            'quantity': quantity,
            'purchase_price': base_price,
            'item_amount': round(base_price * quantity, 2)
        })
    
    # Формирование полного набора данных
    test_data = {
        'recipient_name': 'Home Sweet Home',
        'recipient_street': 'Perekopskaya Street 123',
        'recipient_postal_code': '73022',
        'recipient_city': 'KHERSON',
        'recipient_country': 'UKRAINE',
        'invoice_date': datetime(2024, 9, 18),
        'customer_number': '29060',
        'invoice_number': '5060007',
        'seller': 'Emanuel Baur Asien/Drittland',
        'contact': 'Anja Konig',
        'agent': '49112',
        'order': '2069354',
        'items': items,
        'correspondence_number': '09-2024',
        'correspondence_date': datetime(2024, 9, 10),
        'correspondence_person': 'Tatjana Parygin',
        'delivery_note_number': '4059965',
        'delivery_date': datetime(2024, 9, 18)
    }
    
    return test_data

if __name__ == '__main__':
    # Генерация тестовых данных с 50 записями
    test_data = generate_test_data(50)
    print(f"Сгенерировано записей: {len(test_data['items'])}")
    
    # Вывод первых 5 записей для проверки
    print("\nПример первых 5 записей:")
    for item in test_data['items'][:5]:
        print(f"{item['item_position']}. {item['product_design']} - {item['parameters']['size']} - {item['parameters']['color']}") 