from socket import socket, AF_INET, SOCK_DGRAM

SERVER_PORT = 12000
BUFFER_SIZE = 2048

if __name__ == "__main__":
    with socket(AF_INET, SOCK_DGRAM) as server_socket:
        server_socket.bind(('', SERVER_PORT))
        print('The server is ready to receive')
        while True:
            message, client_address = server_socket.recvfrom(BUFFER_SIZE)
            modified_message = message.upper()
            server_socket.sendto(modified_message, client_address)
