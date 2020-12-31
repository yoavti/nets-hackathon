from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM, SOL_SOCKET, SO_REUSEPORT, SO_BROADCAST
from string_message import BUFFER_SIZE, send_string, recv_string
from offer_message import unpack_offer, OFFER_PORT, create_offer_socket
from multiprocessing import Process
from ANSI import annotate_variable, print_error
import getch


TEAM_NAME = 'Silverhand'


def send_keys(sock):
    'Sends keystrokes by the client to the server'
    while True:
        key = getch.getch()
        try:
            send_string(sock, key)
        except:
            break


def client_round():
    # Looking for server
    print('Listening for offer requests')
    # Setting up UDP socket used for receiving offer messages
    offer_socket = create_offer_socket()
    with offer_socket:
        offer_socket.bind(('', OFFER_PORT))
        # Waiting for offers
        message, server_address = offer_socket.recvfrom(BUFFER_SIZE)
    server_port = unpack_offer(message)
    server_ip, _ = server_address
    if not server_port:
        print_error('Incorrect offer message format received')
        return
    print(
        f'Received offer from {annotate_variable(server_ip)}, attempting to connect...')
    # Setting up TCP socket used for sending keystrokes
    with socket(AF_INET, SOCK_STREAM) as game_socket:
        # Connecting to server
        try:
            game_socket.connect((server_ip, server_port))
        except:
            print_error('Failed to connect to server')
            return
        # Sending team name (with \n at the end)
        try:
            send_string(game_socket, TEAM_NAME + '\n')
        except:
            print_error('Failed to send team name')
            return
        print("Connected and waiting for game to start")
        # Game mode
        try:
            start_message = recv_string(game_socket)
            if not start_message:
                print_error('Could not receive start message for the game')
                return
            print(start_message)
        except:
            print_error('Could not receive start message for the game')
            return
        key_sender = Process(target=send_keys, args=(game_socket,))
        key_sender.start()
        # Trying to receive string messages from server
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


def main():
    print('Client started')
    while True:
        client_round()


if __name__ == "__main__":
    main()
