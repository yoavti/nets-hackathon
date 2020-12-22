from socket import socket, AF_INET, SOCK_DGRAM

HOST = '127.0.0.1'
SERVER_PORT = 12000
BUFFER_SIZE = 2048

if __name__ == "__main__":
    with socket(AF_INET, SOCK_DGRAM) as client_socket:
        message = input('Input lowercase sentence: ').encode('utf-8')
        client_socket.sendto(message, (HOST, SERVER_PORT))
        modified_message, server_address = client_socket.recvfrom(BUFFER_SIZE)
        print(modified_message)
