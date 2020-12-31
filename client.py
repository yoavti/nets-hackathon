from ANSI import print_error, annotate_variable
from socket import socket, AF_INET, SOCK_STREAM
from offer_message import create_offer_socket, OFFER_PORT, unpack_offer
from string_message import BUFFER_SIZE, send_string, recv_string
from multiprocessing import Process
import getch


TEAM_NAME = 'Silverhand'


def receive_server_messages(sock):
    'Receives messages from the server and prints them'
    while try_receiving_server_message(sock):
        pass


def send_keys(sock):
    'Sends keystrokes by the client to the server'
    while True:
        key = getch.getch()
        try:
            send_string(sock, key)
        except:
            break


def play_game(sock):
    'Play the game, which is split into two parallel processes: send_keys and receive_server_messages'
    key_sender = Process(target=send_keys, args=(sock,))
    key_sender.start()
    receive_server_messages(sock)
    key_sender.terminate()


def try_receiving_server_message(sock):
    'Tries receiving a message from the server and returns whether it succeeded'
    try:
        server_message = recv_string(sock)
        if not server_message:
            return False
        print(server_message)
        return True
    except:
        return False


def connect_to_server(sock, server_ip, server_port):
    'Connect to the server over TCP through the given socket and sent team name through it'
    # Connecting over TCP
    try:
        sock.connect((server_ip, server_port))
    except:
        print_error('Failed to connect to server')
        return False
    # Sending team name (with \n at the end)
    try:
        send_string(sock, TEAM_NAME + '\n')
    except:
        print_error('Failed to send team name')
        return False
    print("Connected and waiting for game to start")
    return True


def receive_server_address():
    'Receives an offer message from the server and returns its address'
    with create_offer_socket() as offer_socket:
        offer_socket.bind(('', OFFER_PORT))
        message, server_address = offer_socket.recvfrom(BUFFER_SIZE)
    server_port = unpack_offer(message)
    server_ip, _ = server_address
    return server_ip, server_port


def client_round():
    'Method representing one client round'
    print('Listening for offer requests')
    server_ip, server_port = receive_server_address()
    if not server_port:
        print_error('Incorrect offer message format received')
        return
    print(
        f'Received offer from {annotate_variable(server_ip)}, attempting to connect...')
    # Setting up TCP socket used for sending keystrokes
    with socket(AF_INET, SOCK_STREAM) as game_socket:
        if not connect_to_server(game_socket, server_ip, server_port):
            return
        # Receive start message
        if not try_receiving_server_message(game_socket):
            print_error('Could not receive start message for the game')
            return
        play_game(game_socket)
    print('Server disconnected')


def main():
    'Main method for the client'
    print('Client started')
    while True:
        client_round()


if __name__ == "__main__":
    main()
