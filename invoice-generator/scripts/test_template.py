import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pdf_templates.feiler_template import FeilerInvoiceTemplate

def generate_template():
    """Генерация шаблона с плейсхолдерами."""
    template = FeilerInvoiceTemplate()
    
    # Данные для шаблона (плейсхолдеры)
    template_data = {
        "products": [
            {
                "pos": "[Position]",
                "design": "[Product Design]",
                "size": "[Size]",
                "color": "[Color]",
                "quantity": "[Qty]",
                "qu": "[Unit]",
                "price": "[Price]",
                "amount": "[Amount]"
            }
        ] * 3  # Показываем 3 примера строк
    }
    
    # Получаем абсолютный путь к директории data/output
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'output')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'template_blank.pdf')
    
    template.render(data=template_data, output_path=output_path)
    print(f"Template generated: {output_path}")

def test_multipage_template():
    """Генерация примера с реальными данными."""
    template = FeilerInvoiceTemplate()
    
    # Тестовые данные для двухстраничного документа
    test_data = {
        # Данные отправителя (повторяются на каждой странице)
        "SENDER": "Ernst Feiler GmbH - Postfach 28 - D-95691 Hohenberg/Eger",
        
        # Данные получателя
        "CUSTOMER_FULL_ADDRESS": """Home Sweet Home
Perekopskaya Street 123
73022 KHERSON
UKRAINE""",
        
        # Данные для правой колонки (повторяются на каждой странице)
        "DATE": "18.09.2024",
        "CUSTOMER_NO": "29060",
        "INVOICE_NO": "5060007",
        "SELLER": "Emanuel Baur Asien/Drittland",
        "CONTACT": "Anja König",
        "AGENT": "49112",
        "ORDER": "2069354",
        "TOTAL_PAGES": "2",
        
        # Данные доставки (только на первой странице)
        "SHIPPING_ADDRESS": """Home Sweet Home
Perekopskaya Street 123
73022 KHERSON
UKRAINE""",
        
        # Дополнительная информация (только на первой странице)
        "VAT_INFO": "Tax free exports to third countries pursuant to § 4(1a) i.c.w. § 6 German VAT Act.",
        "CORRESPONDENCE": "Your Correspondence Number 09-2024 dated 10.09.2024 placed by Tatjana Parygin",
        "DELIVERY_NOTE": "Delivery Note No. 4059965, Delivery Date 18.09.2024",
        
        # Товары
        "products": []
    }
    
    # Добавляем товары
    base_product = {
        "pos": "1",
        "design": "BELLE FLEUR",
        "size": "50/100",
        "color": "147 pebble",
        "quantity": "2",
        "qu": "PC",
        "price": "20,30",
        "amount": "40,60"
    }
    
    # Генерируем 11 товаров для двух страниц
    for i in range(11):
        product = base_product.copy()
        product.update({
            "pos": str(i + 1),
            "size": "75/150" if i % 2 == 0 else "50/100",
            "price": "43,00" if i % 2 == 0 else "20,30",
            "amount": "86,00" if i % 2 == 0 else "40,60",
        })
        test_data["products"].append(product)
    
    # Получаем абсолютный путь к директории data/output
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'output')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'example_invoice.pdf')
    
    template.render(data=test_data, output_path=output_path)
    print(f"Example invoice generated: {output_path}")

if __name__ == "__main__":
    generate_template()
    test_multipage_template() 