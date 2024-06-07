# signature_crawler
Проект для PT-INT3

# TCP-сервер и клиент

Этот проект реализует многопоточный TCP-сервер и однопоточный консольный клиент для отправки запросов в формате JSON. Сервер обрабатывает два типа запросов:
1. `CheckLocalFile` - Проверяет указанный файл на наличие заданной сигнатуры и возвращает список смещений, где была найдена сигнатура. Если смещения не найдены, ответ будет {"offsets": "not found"}. Сигнатура представлена в виде набора байт длиной до 1Кб.
2. `QuarantineLocalFile` - Перемещает указанный файл в карантин (специальный каталог, указанный в параметрах запуска сервера).

## Требования

- Python 3.x
- Библиотека argparse (входит в стандартную библиотеку Python)
- Библиотека socket (входит в стандартную библиотеку Python)
- Библиотека logging (входит в стандартную библиотеку Python)

## Установка

Клонируйте репозиторий и перейдите в директорию проекта.

```bash
git clone <https://github.com/dershtal/signature_crawler>
cd <signature_crawler>
```

Сервер

Запустите сервер с помощью следующей команды:
```bash
python server.py --host <host> --port <port> --threads <number_of_threads> --quarantine <quarantine_directory> [--logging]
```
Пример 1:
Запустите сервер с включенным логированием:
```bash
python server.py --host 127.0.0.1 --port 8888 --threads 8 --quarantine ./quarantine --logging
```

Пример 2:
Запустите сервер с настройками по умолчанию:
```bash
python server.py
```

Клиент

Отправьте запросы на сервер с помощью следующей команды:

Пример:
```bash
python client.py <command> <params>
```

Проверка локального файла на наличие сигнатуры:
```bash
python client.py CheckLocalFile '{"file_path": "test.txt", "signature": "6d70 6f72 7420"}'
```
Перемещение локального файла в карантин:
```bash
python client.py QuarantineLocalFile '{"file_path": "test.txt"}'
```

# Завершение работы
Сервер можно аккуратно завершить, отправив сигнал SIGINT (Ctrl+C) из командной строки

# Лицензия
Этот проект лицензирован по лицензии BSD 3.

License
This project is licensed under the BSD 3 License.
