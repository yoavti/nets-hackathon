from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM, SOL_SOCKET, SO_REUSEPORT, SO_BROADCAST
from string_message import BUFFER_SIZE, send_string, recv_string
from offer_message import pack_offer
from time import sleep, time
from random import choice
from multiprocessing import Process, Queue
from scapy.all import get_if_addr
from recordtype import recordtype
from ANSI import annotate_variable, annotate_name, annotate_underline, print_error, print_warning
from time import time


NETWORK = '255.255.255.255'  # TODO: change to something specific to the dev network
HOST = get_if_addr('eth1')
OFFER_PORT = 13117
BACKLOG = 1
DURATION = 10
DELAY_BETWEEN_OFFERS = 1
NUM_OF_TEAMS = 2
TEAMS = [x + 1 for x in range(NUM_OF_TEAMS)]


Player = recordtype('Player', 'socket address name team score')


def manage_player(player, q):
    """
    Method given to a process for the given player.
    Is charged with receiving messages notifying of keys pressed by the client
    and increasing their score.
    """
    while True:
        try:
            msg = recv_string(player.socket)
            if not msg:
                print_error(
                    f'Failed to receive message from client {annotate_name(player.name)}')
                break
            if len(msg) == 1:
                q.put((player.name, msg))
        except:
            print_error(
                f'Failed to receive message from client {annotate_name(player.name)}')
            break


def send_offer(offer_socket, port):
    'Method given to a process charged with sending offer messages through the given socket every second'
    while True:
        # Sending offer to all clients in the network
        try:
            offer_socket.sendto(
                pack_offer(port),
                (NETWORK, OFFER_PORT))
        except:
            print_warning('Failed to send offer messages')
            pass
        sleep(DELAY_BETWEEN_OFFERS)


if __name__ == "__main__":
    print(
        f'Server started, listening on IP address {annotate_variable(HOST)}')
    while True:
        players = []
        # Waiting for clients
        print('Sending out offer requests')
        with socket(AF_INET, SOCK_STREAM) as join_socket:
            join_socket.bind(('', 0))
            join_socket.listen(BACKLOG)
            join_socket.settimeout(DURATION)
            with socket(AF_INET, SOCK_DGRAM) as offer_socket:
                offer_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
                offer_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
                join_port = join_socket.getsockname()[1]
                offer_sender = Process(
                    target=send_offer,
                    args=(offer_socket, join_port,))
                offer_sender.start()
                # Waiting for clients to respond
                start_time = time()
                while time() - start_time < DURATION:
                    try:
                        client_socket, client_address = join_socket.accept()
                        team_name = recv_string(client_socket).rstrip()
                        # Setting some auxilliary parameters
                        team = choice(TEAMS)
                        score = 0
                        # Adding a new Player object to our list of registered players
                        players.append(Player(
                            client_socket,
                            client_address,
                            team_name,
                            team,
                            score))
                    except:
                        break
            offer_sender.terminate()

        def player_names_of_team(team):
            'Returns the names of all players in the team joined by \\n.'
            return '\n'.join([
                annotate_name(player.name)
                for player in players
                if player.team == team])
        # Game mode
        # Sending start message to all registered clients
        members_string = '\n'.join([
            '\n'.join([
                f'Group {annotate_variable(team)}:',
                f'{player_names_of_team(team)}'
            ])
            for team in TEAMS])
        start_message = '\n'.join([
            'Welcome to Keyboard Spamming Battle Royale.',
            f'{members_string}',
            'Start pressing keys on your keyboard as fast as you can!'
        ])
        print(start_message)

        def try_sending_start_message(player, start_message):
            try:
                send_string(player.socket, start_message)
                return True
            except:
                return False
        players = [
            player
            for player in players
            if try_sending_start_message(player, start_message)]
        # Starting game by starting processes which will deal with each clients key-mashing
        q = Queue()
        processes = [
            Process(target=manage_player, args=(player, q,))
            for player in players]
        for p in processes:
            p.start()
        # Waiting for game to end in 10 seconds
        sleep(DURATION)
        # Ending the game
        for p in processes:
            p.terminate()
        # Post-game analysis
        key_histogram = {}
        while not q.empty():
            name, key = q.get()
            if key in key_histogram:
                key_histogram[key] += 1
            else:
                key_histogram[key] = 0
            for player in players:
                if player.name == name:
                    player.score += 1
        ordered_players = sorted(
            players,
            key=lambda player: player.score,
            reverse=True)
        leaderboard = [
            f'{annotate_name(player.name)}\t{annotate_variable(player.score)}'
            for player in ordered_players]
        leaderboard[0] = annotate_underline(leaderboard[0])
        leaderboard_string = '\n'.join(leaderboard)
        common_key = max(key_histogram, key=key_histogram.get)
        scores = [
            sum([
                player.score
                for player in players
                if player.team == team])
            for team in TEAMS]
        winner = 1 + scores.index(max(scores))
        # Sending end message to all registered clients
        scores_string = ' '.join([
            f'Group {annotate_variable(index + 1)} typed in {annotate_variable(score)} characters.'
            for index, score in enumerate(scores)])
        end_message = '\n'.join([
            'Game over!',
            f'{scores_string}',
            f'Group {annotate_variable(winner)} wins!',
            'Congratulations to the winners:',
            f'{player_names_of_team(winner)}',
            'Leaderboard for this round:',
            f'{leaderboard_string}',
            f'The most commonly typed character was {annotate_name(common_key)}'
        ])
        print(end_message)
        for player in players:
            try:
                send_string(player.socket, end_message)
            except:
                print_warning(
                    f'Could not send end message to {annotate_name(player.name)}')
                pass
        # Closing the TCP connections
        for player in players:
            player.socket.close()
        print('​Game over')
