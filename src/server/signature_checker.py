import os

class SignatureChecker:
    """Класс для проверки файлов на наличие сигнатур"""
    def check_file_signature(self, file_path, signature_hex):
        """
        Проверяет файл на наличие сигнатуры
        
        Args:
            file_path (str): Путь к файлу
            signature_hex (str): Сигнатура в hex формате
            
        Returns:
            dict: Результат проверки с офсетами или ошибкой
        """
        if not os.path.exists(file_path):
            return {"error": "File not found"}

        try:
            signature = bytes.fromhex(signature_hex)
            offsets = []

            with open(file_path, "rb") as file:
                content = file.read()
                offset = content.find(signature)
                while offset != -1:
                    offsets.append(offset)
                    offset = content.find(signature, offset + 1)

            if offsets:
                return {"offsets": offsets}
            else:
                return {"offsets": "not found"}

        except Exception as e:
            return {"error": f"Error checking signature: {str(e)}"}
