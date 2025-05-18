import psycopg2
from psycopg2.extras import RealDictCursor

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

def debug_product_parameters(product_id):
    """Получает и выводит параметры продукта для отладки."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Получаем параметры продукта
            cur.execute("""
                SELECT 
                    p.id,
                    p.name,
                    p.sku,
                    get_product_attribute_values_only_string(p.id) AS parameters
                FROM products p
                WHERE p.id = %s
            """, (product_id,))
            
            product = cur.fetchone()
            if product:
                print("\nИнформация о продукте:")
                print(f"ID: {product['id']}")
                print(f"Название: {product['name']}")
                print(f"SKU: {product['sku']}")
                print("\nПараметры (raw):")
                print(f"Тип: {type(product['parameters'])}")
                print(f"Значение: {repr(product['parameters'])}")
                
                if product['parameters']:
                    print("\nПопытка разбора параметров:")
                    try:
                        params = dict(param.strip().split(': ') for param in product['parameters'].split(', '))
                        print("Разобранные параметры:", params)
                    except Exception as e:
                        print(f"Ошибка при разборе параметров: {e}")
            else:
                print(f"Продукт с ID {product_id} не найден")
            
    finally:
        conn.close()

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("Использование: python debug_parameters.py <product_id>")
        sys.exit(1)
    
    product_id = int(sys.argv[1])
    debug_product_parameters(product_id) 