import socket
import logging
from typing import Optional
from dataclasses import dataclass
from .worker import WorkerPool
from .handler import RequestHandler

@dataclass
class ServerConfig:
    """Конфигурация сервера"""
    host: str
    port: int
    thread_count: int
    enable_logging: bool = False
    socket_backlog: int = 5
    socket_reuse_addr: bool = True

class TCPServer:
    """TCP сервер для обработки клиентских соединений"""
    
    def __init__(self, config: ServerConfig, request_handler: RequestHandler) -> None:
        self.config = config
        self.request_handler = request_handler
        self.server_socket: Optional[socket.socket] = None
        self.worker_pool = WorkerPool(config.thread_count, request_handler)
        self.running = False
    
    def start(self) -> None:
        """Запускает сервер"""
        self._setup_socket()
        self._log_startup()
        
        self.worker_pool.start()
        self.running = True
        
        try:
            self._accept_connections()
        except OSError:
            # Сокет был закрыт
            pass
    
    def shutdown(self) -> None:
        """Завершает работу сервера"""
        print("Shutting down server")
        if self.config.enable_logging:
            logging.info("Shutting down server")
        
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        self.worker_pool.stop()
    
    def _setup_socket(self) -> None:
        """Настраивает серверный сокет"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        if self.config.socket_reuse_addr:
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.server_socket.bind((self.config.host, self.config.port))
        self.server_socket.listen(self.config.socket_backlog)
    
    def _log_startup(self) -> None:
        """Логирует информацию о запуске сервера"""
        startup_message = f"Starting server on {self.config.host}:{self.config.port} with {self.config.thread_count} threads"
        print(startup_message)
        
        if self.config.enable_logging:
            logging.info(startup_message)
    
    def _accept_connections(self) -> None:
        """Принимает входящие соединения"""
        while self.running:
            client_socket, client_address = self.server_socket.accept()
            connection_message = f"Connection from {client_address}"
            print(connection_message)
            
            if self.config.enable_logging:
                logging.info(connection_message)
            
            self.worker_pool.add_task(client_socket)