from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM
from string_message import BUFFER_SIZE, send_string, recv_string
from offer_message import pack_offer
from time import sleep, time
from collections import namedtuple
from random import choice
from multiprocessing import Process
from scapy.all import get_if_addr


NETWORK = 'eth1'
HOST = get_if_addr(NETWORK)
OFFER_PORT = 13117
JOIN_PORT = 12000
BACKLOG = 1
NUM_OF_TEAMS = 2
TEAMS = [x + 1 for x in range(NUM_OF_TEAMS - 1)]


Player = namedtuple('Player', 'socket address name team score')


def manage_player(player):
    """
    Method given to a process for the given player.
    Is charged with receiving messages notifying of keys pressed by the client
    and increasing their score."""
    while True:
        player.socket.recv(BUFFER_SIZE)
        player.score = player.score + 1


def send_offer(offer_socket):
    'Method given to a process charged with sending offer messages through the given socket every second'
    while True:
        # Sending offer to all clients in the network
        offer_socket.sendto(
            pack_offer(JOIN_PORT),
            (NETWORK, OFFER_PORT))
        sleep(1)


if __name__ == "__main__":
    print(f'Server started, listening on IP address {HOST}')
    while True:
        players = []
        start_time = time()
        # Waiting for clients
        with socket(AF_INET, SOCK_DGRAM) as offer_socket:
            offer_sender = Process(target=send_offer, args=(offer_socket))
            offer_sender.start()
            time_left = 10
            while time_left > 0:
                # Waiting for clients to reciprocate
                with socket(AF_INET, SOCK_STREAM) as join_socket:
                    join_socket.bind(('', JOIN_PORT))
                    join_socket.listen(BACKLOG)
                    join_socket.settimeout(time_left)
                    try:
                        client_socket, client_address = join_socket.accept()
                    except:
                        pass
                # Waiting for accepted client to sent their team name
                team_name = recv_string(client_socket).rstrip()
                # Setting some auxilliary parameters
                team = choice(TEAMS)
                score = 0
                # Adding a new Player tuple to our list of registered players
                players.append(Player._make((
                    client_socket,
                    client_address,
                    team_name,
                    team,
                    score)))
                time_left = time() - start_time - 10
            offer_sender.terminate()

        def player_names_of_team(team):
            'Returns the names of all players in the team joined by \\n.'
            return '\n'.join([
                player.name
                for player in players
                if player.team == team])
        # Game mode
        # Sending start message to all registered clients
        members_string = '\n'.join([
            f"""
            Group {team}:
            ==
            {player_names_of_team(team)}"""
            for team in TEAMS])
        start_message = f"""
        Welcome to Keyboard Spamming Battle Royale.
        {members_string}
        Start pressing keys on your keyboard as fast as you can!!"""
        print(start_message)
        for player in players:
            send_string(player.socket, start_message)
        # Starting game by starting processes which will deal with each clients key-mashing
        processes = [
            Process(target=manage_player, args=(player))
            for player in players]
        for p in processes:
            p.start()
        # Waiting for game to end in 10 seconds
        sleep(10)
        # Ending the game
        for p in processes:
            p.terminate()
        # Post-game analysis
        scores = [
            sum([
                player.score
                for player in players
                if player.team == team])
            for team in TEAMS]
        winner = 1 + scores.index(max(scores))
        # Sending end message to all registered clients
        scores_string = ' '.join([
            f'Group {index + 1} typed in {score} characters.'
            for index, score in enumerate(scores)])
        end_message = f"""
        Game over!
        {scores_string}
        Congratulations to the winners:
        ==
        {player_names_of_team(winner)}"""
        print(end_message)
        for player in players:
            send_string(player.socket, end_message)
            player.socket.close()
        print('​ Game over, sending out offer requests...')
