from abc import ABC, abstractmethod

class BaseInvoiceTemplate(ABC):
    """Базовый класс для всех шаблонов инвойсов."""
    
    @abstractmethod
    def render(self, data: dict, output_path: str):
        """
        Генерирует PDF-документ на основе данных.
        
        Args:
            data: Словарь с данными для заполнения шаблона
            output_path: Путь для сохранения PDF
        """
        pass 