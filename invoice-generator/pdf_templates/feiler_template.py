from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import black
from reportlab.lib.utils import ImageReader
import os
import platform
from . import BaseInvoiceTemplate

class FeilerInvoiceTemplate(BaseInvoiceTemplate):
    """Шаблон для инвойсов компании Feiler."""

    def __init__(self):
        """Инициализация шаблона и регистрация шрифтов."""
        # Используем шрифт Liberation Serif (свободная замена Times New Roman)
        font_path = os.path.join(os.path.dirname(__file__), '..', 'fonts')
        
        # Проверяем наличие шрифта Liberation
        liberation_regular = os.path.join(font_path, 'LiberationSerif-Regular.ttf')
        liberation_bold = os.path.join(font_path, 'LiberationSerif-Bold.ttf')
        
        if os.path.exists(liberation_regular) and os.path.exists(liberation_bold):
            pdfmetrics.registerFont(TTFont('LiberationSerif', liberation_regular))
            pdfmetrics.registerFont(TTFont('LiberationSerif-Bold', liberation_bold))
            self.font_name = 'LiberationSerif'
            self.font_bold = 'LiberationSerif-Bold'
        else:
            print("Warning: Liberation fonts not found, using system fonts")
            self.font_name = 'Helvetica'
            self.font_bold = 'Helvetica-Bold'
            
        # Путь к логотипу
        self.logo_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample', 'logo_feiler.png')

    def draw_header(self, canvas, width, height, data):
        """Отрисовка шапки документа."""
        # 1. Логотип в правом верхнем углу
        if os.path.exists(self.logo_path):
            img = ImageReader(self.logo_path)
            # Увеличенные размеры логотипа
            logo_width = 180
            logo_height = 70
            # Позиционирование логотипа справа вверху с отступами
            logo_x = width - logo_width - 30
            logo_y = height - logo_height - 20
            canvas.drawImage(img, logo_x, logo_y,
                           width=logo_width, height=logo_height, mask='auto')

        # Начальная позиция для колонок (под логотипом)
        start_y = height - logo_height - 50

        # 2. Левая колонка (адрес отправителя и получателя)
        # Адрес отправителя (подчеркнутый)
        canvas.setFont(self.font_name, 7)
        sender = data.get("SENDER", "Ernst Feiler GmbH - Postfach 28 - D-95691 Hohenberg/Eger")
        canvas.drawString(30, start_y, sender)
        canvas.line(30, start_y - 2, 30 + canvas.stringWidth(sender, self.font_name, 7), start_y - 2)
        
        # Адрес получателя
        canvas.setFont(self.font_name, 10)
        y = start_y - 20
        address_template = data.get("CUSTOMER_FULL_ADDRESS", """[Company Name]
[Street Address]
[Postal Code] [City]
[Country]""")
        for line in address_template.split('\n'):
            canvas.drawString(30, y, line)
            y -= 12

        # 3. Правая колонка (с отступом от правого края)
        # Заголовок Invoice (подчеркнутый)
        right_column_x = width - 250  # Отступ от правого края
        canvas.setFont(self.font_bold, 12)
        invoice_text = "Invoice"
        invoice_y = start_y + 15
        canvas.drawString(right_column_x, invoice_y, invoice_text)
        canvas.line(right_column_x, invoice_y - 2, 
                   right_column_x + canvas.stringWidth(invoice_text, self.font_bold, 12), 
                   invoice_y - 2)

        # Информация в правой колонке
        y = start_y - 5
        fields = [
            ("Date", data.get("DATE", "[Date]")),
            ("Your Customer No.", data.get("CUSTOMER_NO", "[Customer No]")),
            ("Invoice-No.", data.get("INVOICE_NO", "[Invoice No]"), True),
            ("Order", data.get("ORDER", "[Order No]")),
            ("Agent", data.get("AGENT", "[Agent]")),
            ("Seller", data.get("SELLER", "[Seller Name]")),
            ("Contact", data.get("CONTACT", "[Contact Name]"))
        ]

        # Позиции для правой колонки (с правильным выравниванием)
        label_x = right_column_x
        value_x = right_column_x + 120  # Отступ для значений

        for label, value, *bold in fields:
            is_bold = bool(bold and bold[0])
            canvas.setFont(self.font_bold if is_bold else self.font_name, 9)
            canvas.drawString(label_x, y, f"{label}:")
            
            # Для длинных значений используем меньший шрифт
            if len(value) > 20:
                canvas.setFont(self.font_name, 8)
            canvas.drawString(value_x, y, value)
            y -= 12

        # Номер страницы (прижат к правому краю колонки)
        y -= 5
        page_text = f"Page {data.get('PAGE', '1')} fr. {data.get('TOTAL_PAGES', '1')}"
        canvas.drawRightString(width - 30, y, page_text)

    def draw_shipping_info(self, canvas, width, height, data, first_page=True):
        """Отрисовка информации о доставке (только на первой странице)."""
        if not first_page:
            return

        # Определяем начальную позицию для блока доставки
        # (ниже обеих колонок из шапки)
        start_y = height - 200  # Увеличенный отступ сверху
            
        # Ship to с подчеркиванием
        canvas.setFont(self.font_bold, 10)
        ship_to_text = "Ship to:"
        canvas.drawString(30, start_y, ship_to_text)
        canvas.line(30, start_y - 2, 30 + canvas.stringWidth(ship_to_text, self.font_bold, 10), start_y - 2)
        
        # Адрес доставки
        y = start_y - 20
        canvas.setFont(self.font_name, 10)
        for line in data.get("SHIPPING_ADDRESS", "").split('\n'):
            canvas.drawString(30, y, line)
            y -= 12
            
        # Дополнительная информация с увеличенными отступами
        y -= 20
        canvas.setFont(self.font_name, 8)
        
        # VAT информация с подчеркиванием
        vat_info = data.get("VAT_INFO", "")
        canvas.drawString(30, y, vat_info)
        canvas.line(30, y - 2, 30 + canvas.stringWidth(vat_info, self.font_name, 8), y - 2)
        
        # Информация о корреспонденции
        y -= 20
        correspondence = data.get("CORRESPONDENCE", "")
        canvas.drawString(30, y, correspondence)
        
        # Информация о доставке
        y -= 15
        delivery = data.get("DELIVERY_NOTE", "")
        canvas.drawString(30, y, delivery)
        
        return y - 25  # Возвращаем позицию для следующего элемента

    def draw_table_header(self, canvas, width, height, y_position):
        """Отрисовка заголовка таблицы товаров."""
        canvas.setFont(self.font_bold, 9)
        
        # Определяем позиции колонок
        headers = [
            (30, 50, "Pos."),
            (60, 180, "Design"),
            (250, 40, "Size"),
            (300, 40, "Color"),
            (350, 40, "Quantity"),
            (400, 30, "QU"),
            (450, 40, "Price"),
            (500, 60, "Amount\n(EUR)")
        ]
        
        # Рисуем линию над заголовками
        canvas.line(25, y_position + 15, width - 25, y_position + 15)
        
        # Отрисовка заголовков с подчеркиванием
        for x, width_col, text in headers:
            # Многострочный текст
            if '\n' in text:
                lines = text.split('\n')
                canvas.drawString(x, y_position + 5, lines[0])
                canvas.drawString(x, y_position - 5, lines[1])
            else:
                canvas.drawString(x, y_position, text)
            
            # Подчеркивание
            canvas.line(x, y_position - 2, x + width_col, y_position - 2)
        
        # Рисуем линию под заголовками
        canvas.line(25, y_position - 10, width - 25, y_position - 10)

    def draw_product_line(self, canvas, y, product):
        """Отрисовка строки с информацией о товаре."""
        if y < 50:  # Проверка на достижение нижней границы страницы
            return y
            
        canvas.setFont(self.font_name, 9)
        
        # Позиции колонок (соответствуют заголовкам)
        positions = {
            'pos': 30,
            'design': 60,
            'size': 250,
            'color': 300,
            'quantity': 350,
            'qu': 400,
            'price': 450,
            'amount': 500
        }
        
        # Отрисовка значений
        canvas.drawString(positions['pos'], y, str(product.get('pos', '')))
        
        # Design может быть длинным, нужно переносить по словам
        design_text = str(product.get('design', ''))
        if len(design_text) > 30:  # Если текст длинный
            words = design_text.split()
            line1 = []
            line2 = []
            current_line = line1
            current_length = 0
            
            for word in words:
                if current_length + len(word) + 1 <= 30:
                    current_line.append(word)
                    current_length += len(word) + 1
                else:
                    current_line = line2
                    current_line.append(word)
                    current_length = len(word) + 1
            
            canvas.drawString(positions['design'], y, ' '.join(line1))
            if line2:
                canvas.drawString(positions['design'], y - 10, ' '.join(line2))
        else:
            canvas.drawString(positions['design'], y, design_text)
        
        canvas.drawString(positions['size'], y, str(product.get('size', '')))
        canvas.drawString(positions['color'], y, str(product.get('color', '')))
        
        # Выравнивание чисел по правому краю
        quantity = str(product.get('quantity', ''))
        qu = str(product.get('qu', ''))
        price = str(product.get('price', ''))
        amount = str(product.get('amount', ''))
        
        canvas.drawRightString(positions['quantity'] + 35, y, quantity)
        canvas.drawString(positions['qu'], y, qu)
        canvas.drawRightString(positions['price'] + 35, y, price)
        canvas.drawRightString(positions['amount'] + 55, y, amount)
        
        # Если был перенос в design, возвращаем позицию с учетом второй строки
        if len(design_text) > 30:
            return y - 22  # Дополнительное место для второй строки
        return y - 12  # Стандартный отступ между строками

    def render_page(self, canvas, width, height, data, page_number, total_pages):
        """Отрисовка одной страницы документа."""
        # Обновляем номер страницы в данных
        data["PAGE"] = str(page_number)
        data["TOTAL_PAGES"] = str(total_pages)
        
        self.draw_header(canvas, width, height, data)
        
        if page_number == 1:
            # Информация о доставке только на первой странице
            y_position = self.draw_shipping_info(canvas, width, height, data)
        else:
            y_position = height - 100
            
        self.draw_table_header(canvas, width, height, y_position)
        
        # Отрисовка товаров
        y = y_position - 30
        products = data.get("products", [])
        start_idx = (page_number - 1) * 10  # 10 товаров на страницу
        end_idx = min(start_idx + 10, len(products))
        
        for product in products[start_idx:end_idx]:
            y = self.draw_product_line(canvas, y, product)
            if y < 50:  # Если достигли нижней границы страницы
                break

    def render(self, data: dict = None, output_path: str = "../data/output/template_invoice.pdf"):
        """Генерация PDF-документа."""
        if data is None:
            data = {}
            
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4
        
        # Определяем количество страниц
        products = data.get("products", [])
        total_pages = (len(products) + 9) // 10  # 10 товаров на страницу
        if total_pages == 0:
            total_pages = 1
            
        # Генерируем страницы
        for page in range(1, total_pages + 1):
            self.render_page(c, width, height, data, page, total_pages)
            if page < total_pages:
                c.showPage()  # Новая страница
                
        c.save()
        print(f"PDF template saved to {output_path}")
        print(f"Using font: {self.font_name}") 