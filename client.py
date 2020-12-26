from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM
from string_message import BUFFER_SIZE, send_string, recv_string
from offer_message import unpack_offer
from multiprocessing import Process
import getch


TEAM_NAME = 'Silverhand'
OFFER_PORT = 13117


def send_keys(sock):
    while True:
        try:
            key = getch.getch()
            send_string(sock, key)
        except:
            break


def receive_messages(sock):
    while True:
        try:
            server_message = recv_string(sock)
            print(server_message)
        except:
            break


if __name__ == "__main__":
    print('Client started, listening for offer requests...')
    while True:
        # Looking for server
        with socket(AF_INET, SOCK_DGRAM) as offer_socket:
            offer_socket.bind(('', OFFER_PORT))
            message, server_address = offer_socket.recvfrom(BUFFER_SIZE)
        server_port = unpack_offer(message)
        server_ip, _ = server_address
        if not server_port:
            break
        # Connecting to a server
        print(
            f'Received offer from {server_ip}, attempting to connect...')
        with socket(AF_INET, SOCK_STREAM) as game_socket:
            game_socket.connect((server_ip, server_port))
            send_string(game_socket, TEAM_NAME + '\n')
            print("Connected and waiting for game to start")
            # Game mode
            start_message = recv_string(game_socket)
            print(start_message)
            key_sender = Process(target=send_keys, args=(game_socket,))
            key_sender.start()
            while True:
                try:
                    server_message = recv_string(game_socket)
                    print(server_message)
                    break
                except:
                    key_sender.terminate()
                    break
            print('Server disconnected, listening for offer requests...')
