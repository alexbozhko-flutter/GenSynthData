#!/usr/bin/env python3
"""
PDF generation script.
Creates PDF documents from templates using prepared data.
"""

import os
import sys
import json
from pathlib import Path

# Добавляем родительскую директорию в PYTHONPATH для импорта модулей
sys.path.append(str(Path(__file__).parent.parent))

from pdf_templates.feiler_template import FeilerInvoiceTemplate

def generate_pdfs():
    """Generate PDF documents using templates."""
    # TODO: Implement PDF generation logic for multiple documents
    pass

def main():
    """Main function for PDF generation."""
    print("Starting PDF generation...")
    
    # Создаем директорию для выходных файлов, если её нет
    output_dir = Path(__file__).parent.parent / "data" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Генерируем шаблонный PDF
    template = FeilerInvoiceTemplate()
    output_path = output_dir / "template_invoice.pdf"
    template.render(data=None, output_path=str(output_path))
    
    print("PDF generation completed.")

if __name__ == "__main__":
    main() 