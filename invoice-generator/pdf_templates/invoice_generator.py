#!/usr/bin/env python3
"""
Unified invoice generator that creates both HTML and PDF versions
using WeasyPrint for PDF conversion.
"""

import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import math


class FeilerInvoiceGenerator:
    """Generator for Feiler invoices in both HTML and PDF formats."""
    
    def __init__(self):
        """Initialize the generator with templates and fonts configuration."""
        self.base_dir = Path(__file__).parent.parent
        self.template_dir = self.base_dir / "data" / "output_html"
        self.font_config = FontConfiguration()
        
        # Setup Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=False
        )
        
        # Load CSS
        self.css_path = self.template_dir / "styles.css"
        
        # Количество товаров на первой и последующих страницах
        self.products_per_first_page = 8
        self.products_per_page = 12
        
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
        
    def generate_html(self, data, output_path):
        """Generate HTML invoice from template and data."""
        template = self.env.get_template("template.html")
        prepared_data = self._prepare_data(data)
        
        # Add paths for resources
        output_path = Path(output_path)
        css_rel_path = os.path.relpath(self.template_dir / "styles.css", output_path.parent)
        logo_rel_path = os.path.relpath(self.base_dir / "data" / "sample" / "logo_feiler.png", output_path.parent)
        
        prepared_data["CSS_PATH"] = css_rel_path.replace("\\", "/")
        prepared_data["LOGO_PATH"] = logo_rel_path.replace("\\", "/")
        
        # Render HTML
        html_content = template.render(**prepared_data)
        
        # Save HTML file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html_content, encoding='utf-8')
        
        print(f"HTML invoice generated: {output_path}")
        return output_path
        
    def generate_pdf(self, html_path, pdf_path, base_url=None):
        """Generate PDF from HTML using WeasyPrint."""
        html_path = Path(html_path)
        pdf_path = Path(pdf_path)
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load CSS
        css = CSS(filename=str(self.css_path), font_config=self.font_config)
        
        # Convert to PDF
        HTML(filename=str(html_path), base_url=base_url).write_pdf(
            str(pdf_path),
            stylesheets=[css],
            font_config=self.font_config
        )
        
        print(f"PDF invoice generated: {pdf_path}")
        return pdf_path
        
    def generate_both(self, data, html_path, pdf_path, base_url=None):
        """Generate both HTML and PDF versions of the invoice."""
        html_path = self.generate_html(data, html_path)
        pdf_path = self.generate_pdf(html_path, pdf_path, base_url)
        return html_path, pdf_path
        
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