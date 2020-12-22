from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM
from offer_message import unpack_offer


OFFER_PORT = 13117
BUFFER_SIZE = 2048
TEAM_NAME = b'Silverhand\n'


if __name__ == "__main__":
    print('Client started, listening for offer requests...')
    while True:
        # Looking for server
        with socket(AF_INET, SOCK_DGRAM) as offer_socket:
            offer_socket.bind(('', OFFER_PORT))
            message, server_address = offer_socket.recvfrom(BUFFER_SIZE)
            print(message)
        server_port = unpack_offer(message)
        if not server_port:
            break
        # Connecting to a server
        print(
            f'Received offer from {server_address}, attempting to connect...')
        with socket(AF_INET, SOCK_STREAM) as game_socket:
            game_socket.connect((server_address, server_port))
            game_socket.send(TEAM_NAME)
        # Game mode
        # play game
        # After finishing game...
