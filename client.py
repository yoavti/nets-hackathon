from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM
from string_message import BUFFER_SIZE, send_string, recv_string
from offer_message import unpack_offer
from pynput.keyboard import Controller, Listener, Key


TEAM_NAME = input('Your team name: ')
OFFER_PORT = 13117


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
            # Game mode
            start_message = recv_string(game_socket)
            print(start_message)

            def on_press(key):
                'Handles keypress events by the user.'
                if key == Key.esc:
                    return False
                char = key.char
                print(char)
                send_string(game_socket, char)
            with Listener(on_press=on_press) as listener:
                listener.start()
                end_message = recv_string(game_socket)
                print(end_message)
                Controller().press(Key.esc)  # Stop listener
