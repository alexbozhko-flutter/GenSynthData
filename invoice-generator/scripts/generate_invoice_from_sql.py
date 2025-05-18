import os
import sys
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import random
import string
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from templates.invoice.feiler.generator import FeilerInvoiceGenerator

def get_db_connection():
    """Создает подключение к базе данных."""
    return psycopg2.connect(
        dbname="latest",
        user="latest",
        password="Ew0L3h3w1eV9r1g2",
        host="188.165.228.146",
        port="5441",
        cursor_factory=RealDictCursor
    )

def read_sql_query(filename):
    """Читает SQL запрос из файла."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sql_path = os.path.join(script_dir, 'sql', filename)
    with open(sql_path, 'r') as f:
        # Удаляем комментарии и лишние пробелы
        lines = []
        for line in f:
            # Пропускаем комментарии
            if line.strip().startswith('--'):
                continue
            # Добавляем непустые строки
            if line.strip():
                lines.append(line.strip())
        return ' '.join(lines)

def fetch_invoice_data(conn, invoice_id):
    """Получает данные инвойса из базы данных."""
    query = read_sql_query('fetch_invoice_data.sql')
    
    with conn.cursor() as cur:
        cur.execute(query, (invoice_id,))
        return cur.fetchall()

def load_colors():
    """Загружает список цветов из файла."""
    colors_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'colors.txt')
    print(f"\nЗагрузка цветов из файла: {colors_file}")
    
    colors = []
    try:
        with open(colors_file, 'r') as f:
            for line in f:
                if line.strip():
                    # Ищем значение в квадратных скобках и остальной текст
                    parts = line.strip().split('] ', 1)
                    if len(parts) == 2:
                        color_id = parts[0].strip('[')  # Убираем открывающую скобку
                        color_name = parts[1].strip()
                        colors.append((color_id, color_name))
        print(f"Загружено цветов: {len(colors)}")
        print("Список цветов:")
        for color_id, color_name in colors:
            print(f"  [{color_id}] {color_name}")
    except Exception as e:
        print(f"Ошибка при загрузке цветов: {str(e)}")
        colors = []
    
    return colors

def get_random_color(colors):
    """Возвращает случайную пару (color_id, color_name) из списка."""
    if not colors:
        return ".", "white"  # Значения по умолчанию, если список цветов пуст
    
    # Выбираем случайный цвет из списка
    color_id, color_name = random.choice(colors)
    
    # Если ID цвета пустой, возвращаем точку
    if not color_id:
        color_id = "."
        
    return color_id, color_name

def parse_parameters(parameters_str):
    """Разбирает строку параметров в формате <Key><Value>;<Key><Value>."""
    # Возвращаем пустые значения, если параметры не указаны
    if not parameters_str:
        return "", "", ""
    
    print(f"\nПарсинг параметров:")
    print(f"Исходная строка: {parameters_str}")
    
    # Инициализируем значения по умолчанию
    size = ""
    color = ""
    color_id = ""
    
    # Разбиваем строку на отдельные параметры
    params = parameters_str.split(';')
    print(f"Разделенные параметры: {params}")
    
    for param in params:
        # Извлекаем ключ и значение из формата <Key><Value>
        if param and '<' in param and '>' in param:
            parts = param.split('><')
            if len(parts) == 2:
                key = parts[0].strip('<')
                value = parts[1].strip('>')
                print(f"Найден параметр: {key} = {value}")
                
                # Определяем, куда записать значение
                if key == 'Size':
                    size = value
                elif key == 'Color':
                    color = value
                elif key == 'ColorID':
                    color_id = value
    
    print(f"Результат парсинга: size='{size}', color='{color}', color_id='{color_id}'")
    return size, color, color_id

def prepare_invoice_data(sql_data):
    """Преобразует данные из SQL в формат для генератора инвойсов."""
    if not sql_data:
        raise ValueError("Нет данных для формирования инвойса")
        
    # Получаем первую запись для общей информации об инвойсе
    first_record = sql_data[0]
    
    # Загружаем список цветов
    colors = load_colors()
    
    # Функция для генерации случайной строки
    def generate_random_string(length):
        chars = string.ascii_letters + string.digits + " "
        return ''.join(random.choice(chars) for _ in range(length))
    
    # Подготавливаем список товаров
    items = []
    for position, record in enumerate(sql_data, 1):
        size, color, color_id = parse_parameters(record['parameters'])
        
        # Если цвет не указан, выбираем случайный
        if not color or not color_id:
            color_id, color = get_random_color(colors)
            # Если ID цвета пустой, заменяем его на точку
            if not color_id:
                color_id = "."
        
        # Генерируем короткую строку для HS-Code с дополнительными 20 символами
        hs_code_text = "63029100 Chenille towels, 100% cotton " + generate_random_string(20)
        
        # Формируем три строки для каждой позиции
        item = {
            'item_position': position,  # Номер позиции
            'lines': [
                {
                    'is_bold': True,  # Первая строка всегда жирным шрифтом
                    'content': {
                        'collection': record['collection_name'].upper(),  # Преобразуем в верхний регистр
                        'size': size,  # Размер из параметров
                        'color_id': color_id,  # ID цвета
                        'quantity': f"{record['quantity']} pcs",  # Количество
                        'price': f"{float(record['purchase_price']):.2f}".replace('.', ','),  # Цена с форматированием
                        'product_type': record['product_type_name']  # Тип продукта
                    }
                },
                {
                    'is_bold': False,  # Вторая строка обычным шрифтом
                    'content': {
                        'prefix': 'Article No.:',
                        'value': record['product_sku'],  # Артикул
                        'color': color  # Название цвета
                    }
                },
                {
                    'is_bold': False,  # Третья строка обычным шрифтом
                    'content': {
                        'prefix': 'HS-Code',
                        'value': hs_code_text  # HS-Code с дополнительными символами
                    }
                }
            ],
            'amount': f"{float(record['item_amount']):.2f}".replace('.', ',')  # Сумма по позиции
        }
        items.append(item)
    
    # Формируем данные для инвойса
    invoice_data = {
        'recipient_name': 'Home Sweet Home',
        'recipient_street': 'Perekopskaya Street 123',
        'recipient_postal_code': '73022',
        'recipient_city': 'KHERSON',
        'recipient_country': 'UKRAINE',
        'invoice_date': first_record['invoice_date'],
        'customer_number': '29060',
        'invoice_number': str(first_record['invoice_in_number']),
        'seller': 'Emanuel Baur Asien/Drittland',
        'contact': 'Anja Konig',
        'agent': '49112',
        'order': '2069354',
        'items': items,
        'correspondence_number': '09-2024',
        'correspondence_date': datetime.now(),
        'correspondence_person': 'Tatjana Parygin',
        'delivery_note_number': '4059965',
        'delivery_date': datetime.now()
    }
    
    return invoice_data

def generate_invoice_from_sql(invoice_id):
    """Генерирует инвойс на основе данных из SQL."""
    try:
        # Подключаемся к базе данных
        conn = get_db_connection()
        
        # Получаем данные из базы
        sql_data = fetch_invoice_data(conn, invoice_id)
        
        # Подготавливаем данные для генератора
        invoice_data = prepare_invoice_data(sql_data)
        
        # Создаем генератор
        generator = FeilerInvoiceGenerator()
        
        # Определяем пути для выходных файлов
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        output_html = os.path.join(output_dir, f'invoice_{invoice_id}.html')
        output_pdf = os.path.join(output_dir, f'invoice_{invoice_id}.pdf')
        
        # Генерируем инвойс
        html_path, pdf_path = generator.generate(invoice_data, output_html, output_pdf)
        
        print(f"\nИнвойс успешно сгенерирован:")
        print(f"HTML: {html_path}")
        print(f"PDF: {pdf_path}")
        
        return html_path, pdf_path
        
    except Exception as e:
        print(f"Ошибка при генерации инвойса: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Использование: python generate_invoice_from_sql.py <invoice_id>")
        sys.exit(1)
        
    invoice_id = int(sys.argv[1])
    generate_invoice_from_sql(invoice_id) 