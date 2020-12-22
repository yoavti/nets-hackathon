from time import sleep
from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM
from offer_message import pack_offer


HOST = '172.1.0.77'
NETWORK = '172.1.0/24'
OFFER_PORT = 13117
GAME_PORT = 12000
BACKLOG = 1
BUFFER_SIZE = 2048


if __name__ == "__main__":
    print(f'Server started, listening on IP address {HOST}')
    with socket(AF_INET, SOCK_STREAM) as game_socket:
        game_socket.bind(('', GAME_PORT))
        game_socket.listen(BACKLOG)
        while True:
            # Waiting for clients
            with socket(AF_INET, SOCK_DGRAM) as offer_socket:
                for i in range(10):
                    offer_socket.sendto(
                        pack_offer(GAME_PORT),
                        (NETWORK, OFFER_PORT))
                    client_socket, client_address = game_socket.accept()
                    with client_socket:
                        team_name = client_socket.recv(BUFFER_SIZE)
                        team_name = team_name.decode('utf-8').rstrip()
                    sleep(1)
            # Game mode
            # manage game
            # After 10 seconds...
