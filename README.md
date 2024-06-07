# signature_crawler
Project for PT-INT3

# TCP Server and Client

This project implements a multithreaded TCP server and a single-threaded console client for sending JSON-formatted requests. The server processes two types of requests:
1. `CheckLocalFile` - Check a specified file for a given signature and return a list of offsets where the signature is found. If no offsets are found, the response will be `{"offsets": "not found"}`. The signature is represented as a set of bytes up to 1KB in size.
2. `QuarantineLocalFile` - Move the specified file to quarantine (a special directory specified in the server startup options).

## Requirements

- Python 3.x
- `argparse` library (part of Python standard library)
- `socket` library (part of Python standard library)
- `logging` library (part of Python standard library)

## Installation

Clone the repository and navigate to the project directory.

```bash
git clone <https://github.com/dershtal/signature_crawler>
cd <signature_crawler>
```

## Requirements

- Python 3.x
- `argparse` library (part of Python standard library)
- `socket` library (part of Python standard library)
- `logging` library (part of Python standard library)

## Installation

Clone the repository and navigate to the project directory.

Server

Start the server with the following command:
```bash
python server.py --host <host> --port <port> --threads <number_of_threads> --quarantine <quarantine_directory> [--logging]
```
Example 1:
Start the server with logging enabled:
```bash
python server.py --host 127.0.0.1 --port 8888 --threads 8 --quarantine ./quarantine --logging
```

Example 2:
Start the server with default settings and selected number of threads:
```bash
python server.py --threads 8
```

Client

Send requests to the server with the following command:

Example:
```bash
python client.py <command> <params>
```

Check a local file for a signature:
```bash
python client.py CheckLocalFile '{"file_path": "test.txt", "signature": "6d70 6f72 7420"}'
```
Quarantine a local file:
```bash
python client.py QuarantineLocalFile '{"file_path": "test.txt"}'
```

Commands
CheckLocalFile
Check a specified file for a given signature and return a list of offsets where the signature is found. If no offsets are found, the response will be {"offsets": "not found"}.

Parameters:
file_path: Path to the file to check.
signature: Signature to search for, represented as a hexadecimal string.
Example:
json
Copy code
{
    "file_path": "test.txt",
    "signature": "68656c6c6f"
}
QuarantineLocalFile
Move the specified file to quarantine (a special directory specified in the server startup options).

Parameters:
file_path: Path to the file to move to quarantine.
Example:
json
Copy code
{
    "file_path": "test.txt"
}
Shutdown
The server can be gracefully shut down by sending a SIGINT signal (Ctrl+C) from the command line.

License
This project is licensed under the BSD 3 License.
