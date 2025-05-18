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

def find_invoice_with_equipment():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    ii.id,
                    ii.created_date,
                    p.id as product_id,
                    get_product_attributes_string_v2(p.id) AS parameters
                FROM invoicesin ii
                JOIN invoiceincontents iic ON ii.id = iic.invoice_in_id
                JOIN products p ON iic.product_id = p.id
                WHERE get_product_attributes_string_v2(p.id) LIKE '%Equipment%'
                LIMIT 1
            """)
            result = cur.fetchone()
            if result:
                print(f"\nНайден инвойс с параметром Equipment:")
                print(f"ID инвойса: {result['id']}")
                print(f"Дата создания: {result['created_date']}")
                print(f"ID продукта: {result['product_id']}")
                print(f"Параметры: {result['parameters']}")
            else:
                print("Инвойсы с параметром Equipment не найдены")
    finally:
        conn.close()

if __name__ == '__main__':
    find_invoice_with_equipment() 