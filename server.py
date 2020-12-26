from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM
from string_message import BUFFER_SIZE, send_string, recv_string
from offer_message import pack_offer
from time import sleep, time
from random import choice
from multiprocessing import Process, Queue
from scapy.all import get_if_addr
from recordtype import recordtype


NETWORK = '127.0.0.1'
HOST = '127.0.0.1'  # get_if_addr(NETWORK)
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
        msg = player.socket.recv(BUFFER_SIZE)
        q.put((player.name, msg))


def send_offer(offer_socket, port):
    'Method given to a process charged with sending offer messages through the given socket every second'
    while True:
        # Sending offer to all clients in the network
        offer_socket.sendto(
            pack_offer(port),
            (NETWORK, OFFER_PORT))
        sleep(DELAY_BETWEEN_OFFERS)


if __name__ == "__main__":
    print(f'Server started, listening on IP address {HOST}')
    while True:
        players = []
        # Waiting for clients
        with socket(AF_INET, SOCK_STREAM) as join_socket:
            join_socket.bind(('', 0))
            join_socket.listen(BACKLOG)
            join_socket.settimeout(DURATION)
            with socket(AF_INET, SOCK_DGRAM) as offer_socket:
                join_port = join_socket.getsockname()[1]
                offer_sender = Process(
                    target=send_offer,
                    args=(offer_socket, join_port,))
                offer_sender.start()
                # Waiting for clients to respond
                while True:
                    try:
                        client_socket, client_address = join_socket.accept()
                        # Waiting for accepted client to sent their team name
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
                player.name
                for player in players
                if player.team == team])
        # Game mode
        # Sending start message to all registered clients
        members_string = '\n'.join([
            f"""
            Group {team}:
            ==
            {player_names_of_team(team)}
            """
            for team in TEAMS])
        start_message = f"""
        Welcome to Keyboard Spamming Battle Royale.
        {members_string}
        Start pressing keys on your keyboard as fast as you can!
        """
        print(start_message)
        for player in players:
            send_string(player.socket, start_message)
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
        score_per_player = {player.name: 0 for player in players}
        while not q.empty():
            name, key = q.get()
            for player in players:
                if player.name == name:
                    player.score += 1
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
        Group {winner} wins!
        Congratulations to the winners:
        ==
        {player_names_of_team(winner)}
        """
        print(end_message)
        for player in players:
            send_string(player.socket, end_message)
        # Closing the TCP connections
        for player in players:
            player.socket.close()
        print('​Game over, sending out offer requests...')
