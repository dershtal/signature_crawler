import threading
from queue import Queue
from typing import Optional
from dataclasses import dataclass
import socket
from .handler import RequestHandler

@dataclass
class WorkerPoolConfig:
    """Конфигурация пула потоков"""
    thread_count: int
    daemon_threads: bool = True

class WorkerPool:
    """Класс для управления пулом рабочих потоков"""
    
    def __init__(self, thread_count: int, request_handler: RequestHandler) -> None:
        self.config = WorkerPoolConfig(thread_count)
        self.request_handler = request_handler
        self.queue: Queue[Optional[socket.socket]] = Queue()
        self.threads: list[threading.Thread] = []
        self.running = False
    
    def start(self) -> None:
        """Запускает пул потоков"""
        self.running = True
        for i in range(self.config.thread_count):
            thread = threading.Thread(
                target=self._worker,
                name=f"Worker-{i+1}",
                daemon=self.config.daemon_threads
            )
            thread.start()
            self.threads.append(thread)
    
    def add_task(self, client_socket: socket.socket) -> None:
        """Добавляет задачу в очередь"""
        if self.running:
            self.queue.put(client_socket)
    
    def stop(self) -> None:
        """Останавливает пул потоков"""
        self.running = False
        
        # Отправляем сигнал завершения всем потокам
        for _ in range(self.config.thread_count):
            self.queue.put(None)
        
        # Ждем завершения всех потоков
        for thread in self.threads:
            thread.join()
    
    def _worker(self) -> None:
        """Рабочий поток"""
        while self.running:
            client_socket = self.queue.get()
            
            if client_socket is None:
                break
            
            try:
                self.request_handler.handle_request(client_socket)
            except Exception as e:
                # Логируем ошибку, но не останавливаем поток
                print(f"Error in worker thread: {e}")
            finally:
                client_socket.close()
                self.queue.task_done()
