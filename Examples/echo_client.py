from socket import socket, AF_INET, SOCK_STREAM

HOST = '127.0.0.1'
SERVER_PORT = 50007
BUFFER_SIZE = 1024
MESSAGE = b'Hello, world'

if __name__ == "__main__":
    with socket(AF_INET, SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, SERVER_PORT))
        client_socket.sendall(MESSAGE)
        data = client_socket.recv(BUFFER_SIZE)
        print(data)
