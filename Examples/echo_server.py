from socket import socket, AF_INET, SOCK_STREAM

SERVER_PORT = 50007
BUFFER_SIZE = 1024
BACKLOG = 1

if __name__ == "__main__":
    with socket(AF_INET, SOCK_STREAM) as server_socket:
        server_socket.bind(('', SERVER_PORT))
        server_socket.listen(BACKLOG)
        connection_socket, addr = server_socket.accept()
        with connection_socket:
            print(f'Connected by {addr}')
            while True:
                data = connection_socket.recv(BUFFER_SIZE)
                if not data:
                    break
                connection_socket.sendall(data)
