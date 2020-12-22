from offer_message import unpack_offer
from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM


OFFER_PORT = 13117
BUFFER_SIZE = 2048


if __name__ == "__main__":
    with socket(AF_INET, SOCK_DGRAM) as offer_socket:
        offer_socket.bind(('', OFFER_PORT))
        while True:
            # Looking for server and connecting to it
            message, server_address = offer_socket.recvfrom(BUFFER_SIZE)
            server_port = unpack_offer(message)
            if not server_port:
                pass
            with socket(AF_INET, SOCK_STREAM) as game_socket:
                game_socket.connect((server_address, server_port))
            # Game mode
            # After finishing game...
