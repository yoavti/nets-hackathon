from socket import socket, AF_INET, SOCK_STREAM

HOST = '127.0.0.1'
SERVER_PORT = 12000
BUFFER_SIZE = 1024

if __name__ == "__main__":
    with socket(AF_INET, SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, SERVER_PORT))
        sentence = input('Input lowercase sentence: ').encode('utf-8')
        client_socket.send(sentence)
        modified_sentence = client_socket.recv(BUFFER_SIZE)
        print(modified_sentence)
