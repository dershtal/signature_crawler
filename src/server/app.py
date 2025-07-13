import argparse
import signal
import sys
import logging
from typing import NoReturn
from server.tcp_server import TCPServer, ServerConfig
from server.quarantine import QuarantineManager
from server.signature_checker import SignatureChecker
from server.handler import RequestHandler

def setup_logging(enable_logging: bool) -> None:
    """Настраивает логирование"""
    if enable_logging:
        logging.basicConfig(
            filename='server.log', 
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

def parse_arguments() -> argparse.Namespace:
    """Парсит аргументы командной строки"""
    parser = argparse.ArgumentParser(description='TCP Server')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Hostname to bind')
    parser.add_argument('--port', type=int, default=8888, help='Port to bind')
    parser.add_argument('--threads', type=int, default=4, help='Number of threads in the pool')
    parser.add_argument('--quarantine', type=str, default='./quarantine', help='Quarantine directory')
    parser.add_argument('--logging', action='store_true', help='Enable logging to server.log')
    
    return parser.parse_args()

def create_server_components(args: argparse.Namespace) -> tuple[TCPServer, callable]:
    """Создает компоненты сервера"""
    # Создание конфигурации
    config = ServerConfig(
        host=args.host,
        port=args.port,
        thread_count=args.threads,
        enable_logging=args.logging
    )
    
    # Инициализация компонентов
    quarantine_manager = QuarantineManager(args.quarantine)
    signature_checker = SignatureChecker()
    request_handler = RequestHandler(signature_checker, quarantine_manager, args.logging)
    
    # Создание сервера
    server = TCPServer(config, request_handler)
    
    # Создание обработчика сигнала завершения
    def shutdown_handler(signum: int, frame) -> NoReturn:
        server.shutdown()
        sys.exit(0)
    
    return server, shutdown_handler

def main() -> None:
    """Главная функция приложения"""
    args = parse_arguments()
    setup_logging(args.logging)
    
    server, shutdown_handler = create_server_components(args)
    
    # Настройка обработки сигнала завершения
    signal.signal(signal.SIGINT, shutdown_handler)
    
    # Запуск сервера
    server.start()

if __name__ == "__main__":
    main()
