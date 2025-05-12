#!/usr/bin/env python3
import os
import sys
from pathlib import Path

def generate_html_invoice(data, template_path, output_path):
    """Генерация HTML инвойса из шаблона."""
    # Чтение шаблона
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Подготовка данных для HTML
    # Преобразование адресов с переносами строк
    customer_address_html = data.get("CUSTOMER_FULL_ADDRESS", "").replace("\n", "<br>")
    shipping_address_html = data.get("SHIPPING_ADDRESS", "").replace("\n", "<br>")
    
    # Генерация HTML таблицы продуктов
    products_html = []
    for product in data.get("products", []):
        row = f"""
        <tr>
            <td class="pos">{product.get('pos', '')}</td>
            <td class="design">{product.get('design', '')}</td>
            <td class="size">{product.get('size', '')}</td>
            <td class="color">{product.get('color', '')}</td>
            <td class="quantity">{product.get('quantity', '')}</td>
            <td class="qu">{product.get('qu', '')}</td>
            <td class="price">{product.get('price', '')}</td>
            <td class="amount">{product.get('amount', '')}</td>
        </tr>
        """
        products_html.append(row)
    
    # Замена плейсхолдеров
    html = template.replace("{{SENDER}}", data.get("SENDER", ""))
    html = html.replace("{{CUSTOMER_FULL_ADDRESS_HTML}}", customer_address_html)
    html = html.replace("{{DATE}}", data.get("DATE", ""))
    html = html.replace("{{CUSTOMER_NO}}", data.get("CUSTOMER_NO", ""))
    html = html.replace("{{INVOICE_NO}}", data.get("INVOICE_NO", ""))
    html = html.replace("{{ORDER}}", data.get("ORDER", ""))
    html = html.replace("{{AGENT}}", data.get("AGENT", ""))
    html = html.replace("{{SELLER}}", data.get("SELLER", ""))
    html = html.replace("{{CONTACT}}", data.get("CONTACT", ""))
    html = html.replace("{{PAGE}}", data.get("PAGE", "1"))
    html = html.replace("{{TOTAL_PAGES}}", data.get("TOTAL_PAGES", "1"))
    html = html.replace("{{SHIPPING_ADDRESS_HTML}}", shipping_address_html)
    html = html.replace("{{VAT_INFO}}", data.get("VAT_INFO", ""))
    html = html.replace("{{CORRESPONDENCE}}", data.get("CORRESPONDENCE", ""))
    html = html.replace("{{DELIVERY_NOTE}}", data.get("DELIVERY_NOTE", ""))
    html = html.replace("{{PRODUCTS_TABLE}}", "\n".join(products_html))
    
    # Сохранение результата
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"HTML invoice generated: {output_path}")

def generate_template():
    """Генерация шаблона с плейсхолдерами."""
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
    
    base_dir = Path(__file__).parent.parent
    template_path = base_dir / "data" / "output_html" / "template.html"
    output_path = base_dir / "data" / "output_html" / "template_blank.html"
    
    generate_html_invoice(template_data, template_path, output_path)

def generate_example():
    """Генерация примера с реальными данными."""
    test_data = {
        "SENDER": "Ernst Feiler GmbH - Postfach 28 - D-95691 Hohenberg/Eger",
        "CUSTOMER_FULL_ADDRESS": """Home Sweet Home
Perekopskaya Street 123
73022 KHERSON
UKRAINE""",
        "DATE": "18.09.2024",
        "CUSTOMER_NO": "29060",
        "INVOICE_NO": "5060007",
        "SELLER": "Emanuel Baur Asien/Drittland",
        "CONTACT": "Anja König",
        "AGENT": "49112",
        "ORDER": "2069354",
        "TOTAL_PAGES": "2",
        "SHIPPING_ADDRESS": """Home Sweet Home
Perekopskaya Street 123
73022 KHERSON
UKRAINE""",
        "VAT_INFO": "Tax free exports to third countries pursuant to § 4(1a) i.c.w. § 6 German VAT Act.",
        "CORRESPONDENCE": "Your Correspondence Number 09-2024 dated 10.09.2024 placed by Tatjana Parygin",
        "DELIVERY_NOTE": "Delivery Note No. 4059965, Delivery Date 18.09.2024",
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
    
    base_dir = Path(__file__).parent.parent
    template_path = base_dir / "data" / "output_html" / "template.html"
    output_path = base_dir / "data" / "output_html" / "example_invoice.html"
    
    generate_html_invoice(test_data, template_path, output_path)

if __name__ == "__main__":
    generate_template()
    generate_example() 