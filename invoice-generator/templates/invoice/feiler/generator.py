import os
from datetime import datetime
from typing import Dict, List, Optional
from decimal import Decimal
import math

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

class FeilerInvoiceGenerator:
    def __init__(self):
        self.template_dir = os.path.dirname(os.path.abspath(__file__))
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
        self.template = self.env.get_template('template.html')
        self.items_per_page = {
            1: 8,  # На первой странице 8 записей
            'other': 12  # На остальных страницах по 12 записей
        }
        
    def format_currency(self, value: float) -> str:
        """Format currency values according to Feiler standards."""
        return f"{value:.2f}"
        
    def format_date(self, date: datetime) -> str:
        """Format date according to Feiler standards."""
        return date.strftime("%d.%m.%Y")
        
    def calculate_total(self, items: List[Dict]) -> float:
        """Calculate total amount from items."""
        return sum(item.get('item_amount', 0.0) for item in items)
        
    def calculate_pages(self, total_items: int) -> int:
        """Calculate total number of pages needed."""
        if total_items <= self.items_per_page[1]:
            return 1
        remaining_items = total_items - self.items_per_page[1]
        return 1 + math.ceil(remaining_items / self.items_per_page['other'])
        
    def split_items_by_pages(self, items: List[Dict]) -> List[List[Dict]]:
        """Split items into pages according to Feiler's layout rules."""
        if not items:
            return [[]]
            
        pages = []
        remaining_items = items[:]
        
        # Первая страница
        first_page = remaining_items[:self.items_per_page[1]]
        pages.append(first_page)
        remaining_items = remaining_items[self.items_per_page[1]:]
        
        # Остальные страницы
        while remaining_items:
            page_items = remaining_items[:self.items_per_page['other']]
            pages.append(page_items)
            remaining_items = remaining_items[self.items_per_page['other']:]
            
        return pages
        
    def prepare_item_data(self, items: List[Dict]) -> List[Dict]:
        """Prepare items data for the template."""
        prepared_items = []
        for item in items:
            # Получаем данные из всех трёх строк
            first_line = item['lines'][0]['content']
            second_line = item['lines'][1]['content']
            third_line = item['lines'][2]['content']
            
            # Каждая 20-я позиция будет иметь пустое поле Color
            position = item['item_position']
            color = '.' if position % 20 == 0 else first_line.get('color_id', '.')
            color_name = '.' if position % 20 == 0 else second_line.get('color', '')
            
            prepared_items.append({
                'position': position,  # Берем position с верхнего уровня
                'design': first_line.get('collection', ''),  # Только название коллекции
                'article_no': second_line.get('value', ''),  # Артикул из второй строки
                'size': first_line.get('size', ''),
                'color': color,  # ID цвета в первой строке или точка для каждой 20-й позиции
                'color_name': color_name,  # Название цвета во второй строке или точка для каждой 20-й позиции
                'quantity': first_line.get('quantity', ''),
                'price': first_line.get('price', '0,00'),
                'amount': item.get('amount', '0,00'),  # Берем amount с верхнего уровня
                'hs_code': f"{third_line.get('prefix', '')}: {third_line.get('value', '')}"  # Полная строка HS-Code
            })
        return prepared_items
        
    def generate(self, data: Dict, output_html: str, output_pdf: str) -> tuple[str, str]:
        """Generate invoice in both HTML and PDF formats."""
        # Подготовка данных для шаблона
        items = data.get('items', [])
        total_amount = self.calculate_total(items)
        total_pages = self.calculate_pages(len(items))
        pages_items = self.split_items_by_pages(items)
        
        # Генерация HTML для каждой страницы
        all_pages_html = []
        for page_num, page_items in enumerate(pages_items, 1):
            is_last_page = page_num == len(pages_items)
            
            template_data = {
                'logo_path': os.path.join(self.template_dir, 'assets', 'feiler_logo.png'),
                'recipient_name': data.get('recipient_name'),
                'recipient_street': data.get('recipient_street'),
                'recipient_postal_code': data.get('recipient_postal_code'),
                'recipient_city': data.get('recipient_city'),
                'recipient_country': data.get('recipient_country'),
                'invoice_date': self.format_date(data.get('invoice_date')),
                'customer_number': data.get('customer_number'),
                'invoice_number': data.get('invoice_number'),
                'seller': data.get('seller'),
                'contact': data.get('contact'),
                'agent': data.get('agent'),
                'order': data.get('order'),
                'items': self.prepare_item_data(page_items),
                'total_amount': self.format_currency(total_amount) if is_last_page else None,
                'correspondence_number': data.get('correspondence_number'),
                'correspondence_date': self.format_date(data.get('correspondence_date')) if data.get('correspondence_date') else '',
                'correspondence_person': data.get('correspondence_person'),
                'delivery_note_number': data.get('delivery_note_number'),
                'delivery_date': self.format_date(data.get('delivery_date')) if data.get('delivery_date') else '',
                'current_page': page_num,
                'total_pages': total_pages,
                'is_first_page': page_num == 1,  # Флаг первой страницы
                'is_last_page': is_last_page,  # Флаг последней страницы
                'shipping_name': data.get('recipient_name'),  # Добавляем данные для shipping info
                'shipping_street': data.get('recipient_street'),
                'shipping_city': f"{data.get('recipient_postal_code')} {data.get('recipient_city')}",
                'shipping_country': data.get('recipient_country')
            }
            
            page_html = self.template.render(**template_data)
            all_pages_html.append(page_html)
            
            # Добавляем разрыв страницы между страницами, кроме последней
            if not is_last_page:
                all_pages_html.append('<div style="page-break-after: always;"></div>')
        
        # Объединяем все страницы в один HTML
        combined_html = '\n'.join(all_pages_html)
        
        # Сохраняем HTML
        with open(output_html, 'w', encoding='utf-8') as f:
            f.write(combined_html)
            
        # Генерация PDF с правильными размерами страницы и шрифтами
        HTML(string=combined_html).write_pdf(
            output_pdf,
            stylesheets=[],
            optimize_size=('fonts', 'images')
        )
        
        return output_html, output_pdf 