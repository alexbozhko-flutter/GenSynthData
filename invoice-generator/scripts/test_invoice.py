#!/usr/bin/env python3
"""
Test script for invoice template (001).
"""

import os
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from templates.invoice.generator import InvoiceGenerator

def test_invoice():
    """Test invoice generation with sample data."""
    generator = InvoiceGenerator()
    
    # Paths for output files
    output_dir = Path(__file__).parent.parent / "data" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    html_dir = output_dir / "html"
    pdf_dir = output_dir / "pdf"
    html_dir.mkdir(exist_ok=True)
    pdf_dir.mkdir(exist_ok=True)
    
    # Тестовые данные
    test_data = {
        "SENDER": "Ernst Feiler GmbH - Postfach 28 - D-95691 Hohenberg/Eger",
        "CUSTOMER_FULL_ADDRESS": "Home Sweet Home\nPerekopskaya Street 123\n73022 KHERSON\nUKRAINE",
        "DATE": "18.09.2024",
        "CUSTOMER_NO": "29060",
        "INVOICE_NO": "5060007",
        "ORDER": "2069354",
        "AGENT": "49112",
        "SELLER": "Emanuel Baur Asien/Drittland",
        "CONTACT": "Anja König",
        "SHIPPING_ADDRESS": "Home Sweet Home\nPerekopskaya Street 123\n73022 KHERSON\nUKRAINE",
        "VAT_INFO": "Tax free exports to third countries pursuant to § 4(1a) i.c.w. § 6 German VAT Act.",
        "CORRESPONDENCE": "Your Correspondence Number 09-2024 dated 10.09.2024 placed by Tatjana Parygin",
        "DELIVERY_NOTE": "Delivery Note No. 4059965, Delivery Date 18.09.2024",
        "products": []
    }
    
    # Генерируем 25 товаров для теста
    for i in range(1, 26):
        product = {
            "pos": str(i),
            "design": "BELLE FLEUR",
            "size": "75/150" if i % 2 == 0 else "50/100",
            "color": "147 pebble",
            "quantity": "2",
            "qu": "PC",
            "price": "43,00" if i % 2 == 0 else "20,30",
            "amount": "86,00" if i % 2 == 0 else "40,60"
        }
        test_data["products"].append(product)
    
    print(f"\nGenerating invoice (Template {generator.TEMPLATE_ID}: {generator.TEMPLATE_NAME})...")
    generator.generate_both(
        test_data,
        html_dir / "invoice_001.html",
        pdf_dir / "invoice_001.pdf"
    )

if __name__ == "__main__":
    test_invoice() 