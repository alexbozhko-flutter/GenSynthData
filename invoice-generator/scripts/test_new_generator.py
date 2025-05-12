#!/usr/bin/env python3
"""
Test script for the new unified invoice generator.
"""

import os
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from pdf_templates.invoice_generator import FeilerInvoiceGenerator

def test_generator():
    """Test both template generation and example invoice generation."""
    generator = FeilerInvoiceGenerator()
    
    # Paths for output files
    output_dir = Path(__file__).parent.parent / "data" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    html_dir = output_dir / "html"
    pdf_dir = output_dir / "pdf"
    html_dir.mkdir(exist_ok=True)
    pdf_dir.mkdir(exist_ok=True)
    
    # Generate template with placeholders
    print("\nGenerating template files...")
    generator.generate_template(
        html_dir / "template_blank.html",
        pdf_dir / "template_blank.pdf"
    )
    
    # Generate example invoice
    print("\nGenerating example invoice...")
    test_data = {
        # Данные отправителя
        "SENDER": "Ernst Feiler GmbH - Postfach 28 - D-95691 Hohenberg/Eger",
        
        # Данные получателя
        "CUSTOMER_FULL_ADDRESS": """Home Sweet Home
Perekopskaya Street 123
73022 KHERSON
UKRAINE""",
        
        # Данные для правой колонки
        "DATE": "18.09.2024",
        "CUSTOMER_NO": "29060",
        "INVOICE_NO": "5060007",
        "SELLER": "Emanuel Baur Asien/Drittland",
        "CONTACT": "Anja König",
        "AGENT": "49112",
        "ORDER": "2069354",
        "TOTAL_PAGES": "2",
        
        # Данные доставки
        "SHIPPING_ADDRESS": """Home Sweet Home
Perekopskaya Street 123
73022 KHERSON
UKRAINE""",
        
        # Дополнительная информация
        "VAT_INFO": "Tax free exports to third countries pursuant to § 4(1a) i.c.w. § 6 German VAT Act.",
        "CORRESPONDENCE": "Your Correspondence Number 09-2024 dated 10.09.2024 placed by Tatjana Parygin",
        "DELIVERY_NOTE": "Delivery Note No. 4059965, Delivery Date 18.09.2024",
        
        # Товары (пример с повторяющимися позициями)
        "products": [
            {
                "pos": str(i),
                "design": "BELLE FLEUR",
                "size": "50/100" if i % 2 == 0 else "75/150",
                "color": "147 pebble",
                "quantity": "2",
                "qu": "PC",
                "price": "20,30" if i % 2 == 0 else "43,00",
                "amount": "40,60" if i % 2 == 0 else "86,00"
            }
            for i in range(1, 12)  # 11 товаров для проверки многостраничности
        ]
    }
    
    generator.generate_both(
        test_data,
        html_dir / "example_invoice.html",
        pdf_dir / "example_invoice.pdf"
    )

if __name__ == "__main__":
    test_generator() 