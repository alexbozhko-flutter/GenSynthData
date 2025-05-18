import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    return psycopg2.connect(
        dbname="latest",
        user="latest",
        password="Ew0L3h3w1eV9r1g2",
        host="188.165.228.146",
        port="5441",
        cursor_factory=RealDictCursor
    )

def get_sample_product():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    p.id,
                    p.name,
                    p.sku
                FROM products p
                LIMIT 1
            """)
            product = cur.fetchone()
            if product:
                print(f"\nНайден продукт:")
                print(f"ID: {product['id']}")
                print(f"Название: {product['name']}")
                print(f"SKU: {product['sku']}")
            else:
                print("Продукты не найдены")
    finally:
        conn.close()

if __name__ == '__main__':
    get_sample_product() 