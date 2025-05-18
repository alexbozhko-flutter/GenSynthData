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

def get_sample_invoice():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    ii.id,
                    ii.created_date,
                    COUNT(iic.id) as items_count
                FROM invoicesin ii
                JOIN invoiceincontents iic ON ii.id = iic.invoice_in_id
                GROUP BY ii.id, ii.created_date
                LIMIT 1
            """)
            invoice = cur.fetchone()
            if invoice:
                print(f"\nНайден инвойс:")
                print(f"ID: {invoice['id']}")
                print(f"Дата создания: {invoice['created_date']}")
                print(f"Количество позиций: {invoice['items_count']}")
            else:
                print("Инвойсы не найдены")
    finally:
        conn.close()

if __name__ == '__main__':
    get_sample_invoice() 