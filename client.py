import socket
import json
import sys

def send_request(command, params):
    # Отправка запроса серверу
    request = {command: params}
    request_json = json.dumps(request)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(("127.0.0.1", 8888))
        client_socket.sendall(request_json.encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        print(f"Response: {response}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python client.py <command> <params>")
        print("Example: python client.py CheckLocalFile '{\"file_path\": \"test.txt\", \"signature\": \"6d70 6f72 7420\"}'")
        sys.exit(1)

    try:
        command = sys.argv[1]
        params = json.loads(sys.argv[2])
        send_request(command, params)
    except json.JSONDecodeError:
        print("Error: Parameters should be in valid JSON format")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
