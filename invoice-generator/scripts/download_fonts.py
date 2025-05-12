import os
import requests
import tarfile
from io import BytesIO
import shutil

def download_liberation_fonts():
    """Загружает шрифты Liberation и устанавливает их в директорию fonts/."""
    
    # URL для загрузки шрифтов
    liberation_url = "https://github.com/liberationfonts/liberation-fonts/files/7261482/liberation-fonts-ttf-2.1.5.tar.gz"
    
    # Создаем директорию fonts если её нет
    font_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fonts')
    os.makedirs(font_dir, exist_ok=True)
    
    try:
        print("Downloading Liberation fonts...")
        response = requests.get(liberation_url)
        response.raise_for_status()
        
        # Создаем временную директорию для распаковки
        temp_dir = os.path.join(font_dir, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Сохраняем архив
        tar_path = os.path.join(temp_dir, 'liberation-fonts.tar.gz')
        with open(tar_path, 'wb') as f:
            f.write(response.content)
        
        # Распаковываем архив
        with tarfile.open(tar_path, 'r:gz') as tar:
            for member in tar.getmembers():
                if member.name.endswith(('LiberationSerif-Regular.ttf', 'LiberationSerif-Bold.ttf')):
                    tar.extract(member, temp_dir)
                    # Перемещаем файл в корень директории fonts/
                    font_name = os.path.basename(member.name)
                    src_path = os.path.join(temp_dir, member.name)
                    dst_path = os.path.join(font_dir, font_name)
                    shutil.move(src_path, dst_path)
        
        # Удаляем временную директорию
        shutil.rmtree(temp_dir)
        print("Fonts downloaded and installed successfully!")
        
    except Exception as e:
        print(f"Error downloading fonts: {e}")
        # Очищаем временную директорию в случае ошибки
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        return False
    
    return True

if __name__ == "__main__":
    download_liberation_fonts() 