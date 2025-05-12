"""
Invoice template (001) package.

This template is used for generating Feiler invoices in both HTML and PDF formats.
"""

from .generator import InvoiceGenerator

__all__ = ['InvoiceGenerator'] 