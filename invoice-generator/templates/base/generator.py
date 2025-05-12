#!/usr/bin/env python3
"""
Base generator class for all document templates.
"""

from pathlib import Path
from abc import ABC, abstractmethod
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import os


class BaseGenerator(ABC):
    """Base class for all document generators."""
    
    TEMPLATE_ID = None  # Should be overridden in subclasses (e.g. '001' for Invoice)
    TEMPLATE_NAME = None  # Should be overridden in subclasses (e.g. 'Invoice')
    
    def __init__(self):
        """Initialize the generator."""
        if not self.TEMPLATE_ID or not self.TEMPLATE_NAME:
            raise ValueError("TEMPLATE_ID and TEMPLATE_NAME must be defined in subclass")
            
        self.base_dir = Path(__file__).parent.parent.parent
        self.template_dir = self._get_template_dir()
        self.font_config = FontConfiguration()
        
        # Setup Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=False
        )
        
        # Load CSS
        self.css_path = self.template_dir / "html" / "styles.css"
        
    def _get_template_dir(self):
        """Get the directory containing template files."""
        return self.base_dir / "templates" / self.__class__.__module__.split('.')[-2]
        
    @abstractmethod
    def _prepare_data(self, data):
        """
        Prepare data for template rendering.
        Should be implemented in subclasses.
        """
        pass
        
    def generate_html(self, data, output_path):
        """Generate HTML document from template and data."""
        template = self.env.get_template("html/template.html")
        prepared_data = self._prepare_data(data)
        
        # Add paths for resources
        output_path = Path(output_path)
        css_rel_path = os.path.relpath(self.css_path, output_path.parent)
        
        prepared_data["CSS_PATH"] = css_rel_path.replace("\\", "/")
        
        # Render HTML
        html_content = template.render(**prepared_data)
        
        # Save HTML file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html_content, encoding='utf-8')
        
        print(f"HTML {self.TEMPLATE_NAME} generated: {output_path}")
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
        
        print(f"PDF {self.TEMPLATE_NAME} generated: {pdf_path}")
        return pdf_path
        
    def generate_both(self, data, html_path, pdf_path, base_url=None):
        """Generate both HTML and PDF versions of the document."""
        html_path = self.generate_html(data, html_path)
        pdf_path = self.generate_pdf(html_path, pdf_path, base_url)
        return html_path, pdf_path
        
    @abstractmethod
    def generate_template(self, html_path, pdf_path):
        """
        Generate template files with placeholders.
        Should be implemented in subclasses.
        """
        pass 