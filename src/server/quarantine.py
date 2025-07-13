import os
import shutil

class QuarantineManager:
    """Класс для управления карантином файлов"""

    def __init__(self, quarantine_dir):
        self.quarantine_dir = quarantine_dir
        self._ensure_quarantine_dir()

    def _ensure_quarantine_dir(self):
        """Создает директорию карантина если она не существует"""
        os.makedirs(self.quarantine_dir, exist_ok=True)

    def quarantine_file(self, file_path):
        """
        Перемещает файл в карантин
        
        Args:
            file_path (str): Путь к файлу для карантина
            
        Returns:
            dict: Результат операции
        """
        if not os.path.exists(file_path):
            return {"error": "File not found"}

        try:
            filename = os.path.basename(file_path)
            quarantine_path = os.path.join(self.quarantine_dir, filename)

            # Если файл с таким именем уже есть в карантине, добавляем суффикс
            counter = 1
            original_quarantine_path = quarantine_path
            while os.path.exists(quarantine_path):
                name, ext = os.path.splitext(original_quarantine_path)
                quarantine_path = f"{name}_{counter}{ext}"
                counter += 1

            shutil.move(file_path, quarantine_path)
            return {
                "status": "File quarantined", 
                "quarantine_path": quarantine_path
            }

        except Exception as e:
            return {"error": f"Error quarantining file: {str(e)}"}
