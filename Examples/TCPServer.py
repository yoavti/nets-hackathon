from socket import socket, AF_INET, SOCK_STREAM

SERVER_PORT = 12000
BUFFER_SIZE = 1024
BACKLOG = 1

if __name__ == "__main__":
    with socket(AF_INET, SOCK_STREAM) as server_socket:
        server_socket.bind(('', SERVER_PORT))
        server_socket.listen(BACKLOG)
        print('The server is ready to receive')
        while True:
            connection_socket, addr = server_socket.accept()
            with connection_socket:
                sentence = connection_socket.recv(BUFFER_SIZE)
                capitalized_sentence = sentence.upper()
                connection_socket.send(capitalized_sentence)
