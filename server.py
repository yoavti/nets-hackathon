from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM
from string_message import BUFFER_SIZE, send_string, recv_string
from offer_message import pack_offer
from time import sleep
from collections import namedtuple
from random import choice
from multiprocessing import Process
from functools import reduce


HOST = '172.1.0.77'
NETWORK = '172.1.0/24'
OFFER_PORT = 13117
JOIN_PORT = 12000
BACKLOG = 1
TEAMS = [1, 2]


Player = namedtuple('Player', 'socket address name team score')


def manage_player(player, start_message):
    send_string(player.socket, start_message)
    while True:
        player.socket.recv(BUFFER_SIZE)
        player.score = player.score + 1


if __name__ == "__main__":
    print(f'Server started, listening on IP address {HOST}')
    while True:
        players = []
        # Waiting for clients
        with socket(AF_INET, SOCK_DGRAM) as offer_socket:
            for i in range(10):
                offer_socket.sendto(
                    pack_offer(JOIN_PORT),
                    (NETWORK, OFFER_PORT))
                with socket(AF_INET, SOCK_STREAM) as join_socket:
                    join_socket.bind(('', JOIN_PORT))
                    join_socket.listen(BACKLOG)
                    client_socket, client_address = join_socket.accept()
                team_name = recv_string(client_socket).rstrip()
                team = choice(TEAMS)
                score = 0
                players.append(Player._make((
                    client_socket,
                    client_address,
                    team_name,
                    team,
                    score)))
                sleep(1)
        # Game mode
        newline = '\n'
        team_members = '\n'.join([
            f"""
            Group {team}:
            ==
            {newline.join([
                player.name
                for player in players
                if player.team == team])}"""
            for team in TEAMS])
        start_message = f"""
        Welcome to Keyboard Spamming Battle Royale.
        {team_members}
        Start pressing keys on your keyboard as fast as you can!!"""
        processes = [
            Process(target=manage_player, args=(player, start_message))
            for player in players]
        for p in processes:
            p.start()
        sleep(10)
        for p in processes:
            p.join()
        scores = [
            reduce(
                lambda acc, curr:
                    acc + (curr.score if curr.team == team else 0),
                players,
                0)
            for team in TEAMS]
        winner = 1 + scores.index(max(scores))
        scores_string = ' '.join([
            f'Group {index + 1} type in {score}.'
            for index, score in enumerate(scores)])
        print(f"""
        Game over!
        {scores_string}
        Congratulations to the winners:
        ==
        {newline.join([
            player.name
            for player in players
            if player.team == winner])}""")
        for player in players:
            player.socket.close()
        print('​ Game over, sending out offer requests...')
