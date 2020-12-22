from time import sleep
from socket import socket, AF_INET, SOCK_DGRAM
from offer_message import pack_offer


HOST = '172.1.0.77'
NETWORK = '172.1.0/24'
OFFER_PORT = 13117
GAME_PORT = 12000


if __name__ == "__main__":
    print(f'Server started, listening on IP address {HOST}')
    while True:
        # Waiting for clients
        with socket(AF_INET, SOCK_DGRAM) as offer_socket:
            for i in range(10):
                offer_socket.sendto(
                    pack_offer(GAME_PORT),
                    (NETWORK, OFFER_PORT))
                sleep(1)
        # Game mode
        # manage game
        # After 10 seconds...
        pass
