from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM
from offer_message import pack_offer
from time import sleep
from collections import namedtuple


HOST = '172.1.0.77'
NETWORK = '172.1.0/24'
OFFER_PORT = 13117
BASE_GAME_PORT = 12000
BACKLOG = 1
BUFFER_SIZE = 2048


Player = namedtuple('Player', 'socket address name score')


if __name__ == "__main__":
    print(f'Server started, listening on IP address {HOST}')
    while True:
        players = []
        # Waiting for clients
        with socket(AF_INET, SOCK_DGRAM) as offer_socket:
            for i in range(10):
                next_available_port = BASE_GAME_PORT + len(players)
                offer_socket.sendto(
                    pack_offer(next_available_port),
                    (NETWORK, OFFER_PORT))
                with socket(AF_INET, SOCK_STREAM) as join_socket:
                    join_socket.bind(('', next_available_port))
                    join_socket.listen(BACKLOG)
                    client_socket, client_address = join_socket.accept()
                with client_socket:
                    team_name = client_socket.recv(BUFFER_SIZE)
                    team_name = team_name.decode('utf-8').rstrip()
                    players.append(Player._make((
                        client_socket,
                        client_address,
                        team_name,
                        0)))
                sleep(1)
        # Game mode
        # manage game
        # After 10 seconds...
