from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM, SOL_SOCKET, SO_REUSEPORT, SO_BROADCAST
from string_message import BUFFER_SIZE, send_string, recv_string
from offer_message import unpack_offer
from multiprocessing import Process
from ANSI import annotate_variable, print_error
import getch


TEAM_NAME = 'Silverhand'
OFFER_PORT = 13117


def send_keys(sock):
    'Method given to a process which is responsible for sending keystrokes to the server'
    while True:
        key = getch.getch()
        try:
            send_string(sock, key)
        except:
            break


if __name__ == "__main__":
    print('Client started')
    while True:
        # Looking for server
        print('Listening for offer requests')
        with socket(AF_INET, SOCK_DGRAM) as offer_socket:
            offer_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
            offer_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
            offer_socket.bind(('', OFFER_PORT))
            message, server_address = offer_socket.recvfrom(BUFFER_SIZE)
        server_port = unpack_offer(message)
        server_ip, _ = server_address
        if not server_port:
            print_error('Incorrect offer message format received')
            continue
        # Connecting to a server
        print(
            f'Received offer from {annotate_variable(server_ip)}, attempting to connect...')
        with socket(AF_INET, SOCK_STREAM) as game_socket:
            # Connecting to server
            try:
                game_socket.connect((server_ip, server_port))
            except:
                print_error('Failed to connect to server')
                continue
            # Sending team name (with \n at the end)
            try:
                send_string(game_socket, TEAM_NAME + '\n')
            except:
                print_error('Failed to send team name')
                continue
            print("Connected and waiting for game to start")
            # Game mode
            try:
                start_message = recv_string(game_socket)
                if not start_message:
                    print_error('Could not receive start message for the game')
                    continue
                print(start_message)
            except:
                print_error('Could not receive start message for the game')
                continue
            key_sender = Process(target=send_keys, args=(game_socket,))
            key_sender.start()
            while True:
                try:
                    server_message = recv_string(game_socket)
                    if not server_message:
                        break
                    print(server_message)
                except:
                    break
            key_sender.terminate()
            print('Server disconnected')
