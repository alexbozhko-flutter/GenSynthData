#!/usr/bin/env python3
"""
Invoice generator implementation.
"""

import os
import math
from pathlib import Path
from ..base.generator import BaseGenerator


class InvoiceGenerator(BaseGenerator):
    """Generator for Feiler invoices."""
    
    TEMPLATE_ID = "001"
    TEMPLATE_NAME = "Invoice"
    
    def __init__(self):
        """Initialize the invoice generator."""
        super().__init__()
        
        # Количество товаров на первой и последующих страницах
        self.products_per_first_page = 8
        self.products_per_page = 12
        
        # Путь к логотипу
        self.logo_path = self.base_dir / "data" / "sample" / "logo_feiler.png"
        
    def _prepare_data(self, data):
        """Prepare data for template rendering."""
        prepared_data = data.copy() if data else {}
        
        # Convert newlines in addresses to HTML breaks
        if "CUSTOMER_FULL_ADDRESS" in prepared_data:
            prepared_data["CUSTOMER_FULL_ADDRESS_HTML"] = prepared_data["CUSTOMER_FULL_ADDRESS"].replace("\n", "<br>")
        if "SHIPPING_ADDRESS" in prepared_data:
            prepared_data["SHIPPING_ADDRESS_HTML"] = prepared_data["SHIPPING_ADDRESS"].replace("\n", "<br>")
            
        # Разделяем товары на страницы
        products = prepared_data.get("products", [])
        
        # Товары для первой страницы
        first_page_products = products[:self.products_per_first_page]
        remaining_products = products[self.products_per_first_page:]
        
        # Генерируем HTML для первой страницы
        first_page_html = []
        for product in first_page_products:
            row = self._generate_product_row(product)
            first_page_html.append(row)
        prepared_data["FIRST_PAGE_PRODUCTS"] = "\n".join(first_page_html)
        
        # Генерируем последующие страницы
        if remaining_products:
            subsequent_pages = []
            total_remaining = len(remaining_products)
            num_subsequent_pages = math.ceil(total_remaining / self.products_per_page)
            
            for page_num in range(num_subsequent_pages):
                start_idx = page_num * self.products_per_page
                end_idx = start_idx + self.products_per_page
                page_products = remaining_products[start_idx:end_idx]
                
                # Генерируем HTML для страницы
                page_html = self._generate_subsequent_page(
                    page_products,
                    page_num + 2,  # +2 потому что первая страница уже есть
                    len(products)
                )
                subsequent_pages.append(page_html)
            
            prepared_data["SUBSEQUENT_PAGES"] = "\n".join(subsequent_pages)
        else:
            prepared_data["SUBSEQUENT_PAGES"] = ""
            
        # Общее количество страниц
        total_pages = 1 + math.ceil(max(0, len(products) - self.products_per_first_page) / self.products_per_page)
        prepared_data["TOTAL_PAGES"] = str(total_pages)
        
        # Добавляем путь к логотипу
        if self.logo_path.exists():
            prepared_data["LOGO_PATH"] = os.path.relpath(
                self.logo_path,
                Path(self.template_dir) / "html"
            ).replace("\\", "/")
            
        return prepared_data
        
    def _generate_product_row(self, product):
        """Generate HTML for a single product row."""
        return f"""
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
        
    def _generate_subsequent_page(self, products, page_num, total_products):
        """Generate HTML for a subsequent page."""
        products_html = []
        for product in products:
            row = self._generate_product_row(product)
            products_html.append(row)
            
        return f"""
    <div class="page subsequent-page">
        <div class="page-header">
            <img src="{{{{LOGO_PATH}}}}" alt="Feiler Logo" class="logo">
            <div class="page-info">
                <div class="invoice-details">
                    <table>
                        <tr>
                            <td class="label">Invoice-No.:</td>
                            <td class="value bold">{{{{INVOICE_NO}}}}</td>
                        </tr>
                        <tr>
                            <td class="label">Date:</td>
                            <td class="value">{{{{DATE}}}}</td>
                        </tr>
                    </table>
                    <div class="page-number">Page {page_num} fr. {{{{TOTAL_PAGES}}}}</div>
                </div>
            </div>
        </div>
        
        <div class="products-table">
            <table>
                <thead>
                    <tr>
                        <th class="pos">Pos.</th>
                        <th class="design">Design</th>
                        <th class="size">Size</th>
                        <th class="color">Color</th>
                        <th class="quantity">Quantity</th>
                        <th class="qu">QU</th>
                        <th class="price">Price</th>
                        <th class="amount">Amount<br>(EUR)</th>
                    </tr>
                </thead>
                <tbody>
                    {chr(10).join(products_html)}
                </tbody>
            </table>
        </div>
    </div>
    """
        
    def generate_template(self, html_path, pdf_path):
        """Generate template files with placeholders."""
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
            ] * 3  # Show 3 example rows
        }
        
        return self.generate_both(template_data, html_path, pdf_path) 