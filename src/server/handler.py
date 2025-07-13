import json
import logging
import socket
from typing import Dict, Any, Optional
from dataclasses import dataclass
from .signature_checker import SignatureChecker
from .quarantine import QuarantineManager

@dataclass
class HandlerConfig:
    """Конфигурация обработчика запросов"""
    enable_logging: bool = False
    buffer_size: int = 1024
    encoding: str = 'utf-8'

class RequestHandler:
    """Класс для обработки клиентских запросов"""
    
    def __init__(
        self, 
        signature_checker: SignatureChecker, 
        quarantine_manager: QuarantineManager,
        enable_logging: bool = False
    ) -> None:
        self.signature_checker = signature_checker
        self.quarantine_manager = quarantine_manager
        self.config = HandlerConfig(enable_logging)
    
    def handle_request(self, client_socket: socket.socket) -> None:
        """
        Обрабатывает запрос от клиента
        
        Args:
            client_socket: Сокет клиента
        """
        try:
            request_data = self._receive_request(client_socket)
            response = self._process_request(request_data)
            self._send_response(client_socket, response)
            
            if self.config.enable_logging:
                command = list(request_data.keys())[0] if request_data else "unknown"
                logging.info(f"Handled command {command} with response {response}")
                
        except Exception as e:
            error_response = {"error": str(e)}
            self._send_response(client_socket, error_response)
            if self.config.enable_logging:
                logging.error(f"Error handling client: {str(e)}")
    
    def _receive_request(self, client_socket: socket.socket) -> Dict[str, Any]:
        """Получает и парсит запрос от клиента"""
        request_bytes = client_socket.recv(self.config.buffer_size)
        request_str = request_bytes.decode(self.config.encoding)
        return json.loads(request_str)
    
    def _process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обрабатывает запрос и возвращает ответ"""
        if not request_data:
            return {"error": "Empty request"}
        
        command = list(request_data.keys())[0]
        params = request_data[command]
        
        if command == "CheckLocalFile":
            return self._handle_check_file(params)
        elif command == "QuarantineLocalFile":
            return self._handle_quarantine_file(params)
        else:
            return {"error": f"Unknown command: {command}"}
    
    def _send_response(self, client_socket: socket.socket, response: Dict[str, Any]) -> None:
        """Отправляет ответ клиенту"""
        response_str = json.dumps(response)
        response_bytes = response_str.encode(self.config.encoding)
        client_socket.sendall(response_bytes)
    
    def _handle_check_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Обрабатывает команду проверки файла"""
        file_path = params.get("file_path")
        signature = params.get("signature", "")
        
        if not file_path:
            return {"error": "Missing file_path parameter"}
        
        return self.signature_checker.check_file_signature(file_path, signature)
    
    def _handle_quarantine_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Обрабатывает команду карантина файла"""
        file_path = params.get("file_path")
        
        if not file_path:
            return {"error": "Missing file_path parameter"}
        
        return self.quarantine_manager.quarantine_file(file_path)
