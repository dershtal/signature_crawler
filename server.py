import socket
import threading
import json
import os
import signal
import sys
from queue import Queue
import argparse
import logging

class TCPServer:
    def __init__(self, host, port, thread_count, quarantine_dir, enable_logging):
        # Инициализация сервера
        self.host = host
        self.port = port
        self.thread_count = thread_count
        self.quarantine_dir = quarantine_dir
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.queue = Queue()
        self.threads = []
        self.enable_logging = enable_logging

        # Настройка логирования, если включено при старте сервера
        if self.enable_logging:
            logging.basicConfig(filename='server.log', level=logging.DEBUG,
                                format='%(asctime)s - %(levelname)s - %(message)s')
            logging.info("Server initialized")

        # Обработка сигнала завершения
        signal.signal(signal.SIGINT, self.shutdown)

    def start(self):
        # Запуск сервера
        print(f"Starting server on {self.host}:{self.port} with {self.thread_count} threads")
        if self.enable_logging:
            logging.info(f"Starting server on {self.host}:{self.port} with {self.thread_count} threads")

        # Создание и запуск потоков-демонов
        for _ in range(self.thread_count):
            thread = threading.Thread(target=self.worker)
            thread.daemon = True
            thread.start()
            self.threads.append(thread)

        # Принятие входящих соединений
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Connection from {client_address}")
            if self.enable_logging:
                logging.info(f"Connection from {client_address}")
            self.queue.put(client_socket)

    def worker(self):
        # Поток-работник для обработки запросов
        while True:
            client_socket = self.queue.get()
            if client_socket is None:
                break
            self.handle_client(client_socket)
            client_socket.close()
            self.queue.task_done()

    def handle_client(self, client_socket):
        # Обработка запроса клиента
        try:
            request = client_socket.recv(1024).decode('utf-8')
            request_data = json.loads(request)
            command = list(request_data.keys())[0]
            params = request_data[command]

            if command == "CheckLocalFile":
                response = self.check_local_file(params)
            elif command == "QuarantineLocalFile":
                response = self.quarantine_local_file(params)
            else:
                response = {"error": "Unknown command"}

            client_socket.sendall(json.dumps(response).encode('utf-8'))
            if self.enable_logging:
                logging.info(f"Handled command {command} with response {response}")
        except Exception as e:
            error_message = {"error": str(e)}
            client_socket.sendall(json.dumps(error_message).encode('utf-8'))
            if self.enable_logging:
                logging.error(f"Error handling client: {str(e)}")

    def check_local_file(self, params):
        # Проверка файла на сигнатуру
        file_path = params.get("file_path")
        signature = bytes.fromhex(params.get("signature", ""))
        offsets = []

        if os.path.exists(file_path):
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
        else:
            return {"error": "File not found"}

    def quarantine_local_file(self, params):
        # Перемещение файла в карантин
        file_path = params.get("file_path")

        if os.path.exists(file_path):
            try:
                os.makedirs(self.quarantine_dir, exist_ok=True)
                quarantine_path = os.path.join(self.quarantine_dir, os.path.basename(file_path))
                os.rename(file_path, quarantine_path)
                return {"status": "File quarantined", "quarantine_path": quarantine_path}
            except Exception as e:
                return {"error": str(e)}
        else:
            return {"error": "File not found"}

    def shutdown(self, signum, frame):
        # Завершение работы сервера
        print("Shutting down server")
        if self.enable_logging:
            logging.info("Shutting down server")
        self.server_socket.close()
        for _ in range(self.thread_count):
            self.queue.put(None)
        for thread in self.threads:
            thread.join()
        sys.exit(0)

if __name__ == "__main__":
    # Чтение параметров командной строки
    parser = argparse.ArgumentParser(description='TCP Server')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Hostname to bind')
    parser.add_argument('--port', type=int, default=8888, help='Port to bind')
    parser.add_argument('--threads', type=int, default=4, help='Number of threads in the pool')
    parser.add_argument('--quarantine', type=str, default='./quarantine', help='Quarantine directory')
    parser.add_argument('--logging', action='store_true', help='Enable logging to server.log')

    args = parser.parse_args()

    # Параметры запуска сервера
    host = args.host
    port = args.port
    thread_count = args.threads
    quarantine_dir = args.quarantine
    enable_logging = args.logging

    # Инициализация и запуск сервера
    server = TCPServer(host, port, thread_count, quarantine_dir, enable_logging)
    server.start()
