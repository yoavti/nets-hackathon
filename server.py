from ANSI import annotate_variable, print_warning, annotate_name, annotate_underline, print_error
from multiprocessing import Queue, Process
from socket import socket, AF_INET, SOCK_STREAM
from offer_message import create_offer_socket, pack_offer, OFFER_PORT
from time import sleep, time
from string_message import recv_string, send_string
from random import choice
from scapy.all import get_if_addr
from recordtype import recordtype


NETWORK_SETTING = 'ssh'
NUM_OF_TEAMS = 2
TEAMS = [x + 1 for x in range(NUM_OF_TEAMS)]
DURATION = 10
DELAY_BETWEEN_OFFERS = 1
BACKLOG = 1
if NETWORK_SETTING == 'home':
    NETWORK = '255.255.255.255'
    HOST = '127.0.0.1'
elif NETWORK_SETTING == 'ssh':
    NETWORK = '172.1.255.255'
    HOST = get_if_addr('eth1')
elif NETWORK_SETTING == 'exam':
    NETWORK = '172.99.255.255'
    HOST = get_if_addr('eth2')
else:
    NETWORK = '255.255.255.255'
    HOST = '127.0.0.1'

Player = recordtype('Player', 'socket address name team score')


def try_sending_message(sock, message):
    'Sends the given string message through the given socket and returns whether the message was sent properly'
    try:
        send_string(sock, message)
        return True
    except:
        return False


def send_message_to_players(message, players, print_fn):
    """
    Input:

    message: string message to send to the players

    players: list of players

    print_fn: function that receives a player name and prints a debug message

    Prints the given message,
    filters the list of players by whether or not the server was able to send the message,
    goes over all players, and if they were filtered, close their connection and print a debug message with their name,
    finally returns the list of players left after the filter.
    """
    print(message)
    players_left = [
        player
        for player in players
        if try_sending_message(player.socket, message)]
    for player in players:
        if player not in players_left:
            player.socket.close()
            print_fn(player.name)
    return players_left


def player_names_of_team(players, team):
    'Returns the names of all players in the team joined by \\n.'
    return '\n'.join([
        annotate_name(player.name)
        for player in players
        if player.team == team])


def send_end_message(players, leaderboard_string, scores, winner, common_key):
    'Sends the start message to the clients'
    scores_string = ' '.join([
        f'Group {annotate_variable(index + 1)} typed in {annotate_variable(score)} characters.'
        for index, score in enumerate(scores)])
    end_message = '\n'.join([
        'Game over!',
        f'{scores_string}',
        f'Group {annotate_variable(winner)} wins!',
        'Congratulations to the winners:',
        f'{player_names_of_team(players, winner)}',
        'Leaderboard for this round:',
        f'{leaderboard_string}',
        f"The most commonly typed character was '{annotate_name(common_key)}'"
    ])
    players = send_message_to_players(
        end_message,
        players,
        lambda name: print_warning(f'Could not send end message to {annotate_name(name)}'))


def generate_leaderboard_string(players):
    """
    Generated a string representation of a
    leaderboard - list of players and their scores ordered by score, for the given list of player
    (after their scores have been calculated, of course)
    """
    ordered_players = sorted(
        players,
        key=lambda player: player.score,
        reverse=True)
    leaderboard = [
        f'{annotate_name(player.name)}\t{annotate_variable(player.score)}'
        for player in ordered_players]
    leaderboard[0] = annotate_underline(leaderboard[0])
    leaderboard_string = '\n'.join(leaderboard)
    return leaderboard_string


def count_keys(players, q):
    'Goes over the given queue and increments the count of appearances of both keys typed by all players and all keys typed by players'
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
    return key_histogram


def post_game_analysis(players, q):
    'Calculate statistics for the given players and queue and finish game'
    # Count the appearances of keys typed by all players and all keys typed by each player
    key_histogram = count_keys(players, q)
    # Creating leaderboard - ordered list of players by score
    leaderboard_string = generate_leaderboard_string(players)
    if key_histogram:
        # Most typed key
        common_key = max(key_histogram, key=key_histogram.get)
    else:
        common_key = 'no keys entered'
    scores = [  # Score for each team
        sum([
            player.score
            for player in players
            if player.team == team])
        for team in TEAMS]
    winner = 1 + scores.index(max(scores))  # Winning team
    send_end_message(
        players,
        leaderboard_string,
        scores,
        winner,
        common_key)
    # Closing the TCP connections
    for player in players:
        player.socket.close()
    print('​Game over')


def manage_player(player, q):
    "Receives messages from the given player's socket and adds them to the queue (while specifying the player's name)"
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


def play_game(players, q):
    """
    Play the game, consisting of:
    starting the process-per-client,
    waiting for game to end in 10 seconds,
    and ending the game by terminating the processes
    """
    # Starting game by starting processes which will deal with each clients key-mashing
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


def send_start_message(players):
    'Sends the start message to the clients'
    members_string = '\n'.join([
        '\n'.join([
            f'Group {annotate_variable(team)}:',
            f'{player_names_of_team(players, team)}'
        ])
        for team in TEAMS])
    start_message = '\n'.join([
        'Welcome to Keyboard Spamming Battle Royale.',
        f'{members_string}',
        'Start pressing keys on your keyboard as fast as you can!'])
    players = send_message_to_players(
        start_message,
        players,
        lambda name: print_warning(f'Could not send start message to {annotate_name(name)}'))


def receive_players(join_socket):
    'Receives player connection and adds details about them to a list'
    players = []
    start_time = time()
    while time() - start_time < DURATION:
        try:
            # Accepting the player's connection
            client_socket, client_address = join_socket.accept()
            # Receiving the team name
            team_name = recv_string(client_socket).rstrip()
            # Selecting a team assignment at random
            team = choice(TEAMS)
            # Setting the score to 0
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
    return players


def send_offers(offer_socket, port):
    'Sends offer messages through the given socket every second'
    while True:
        # Sending offer to all clients in the network
        try:
            offer_socket.sendto(
                pack_offer(port),
                (NETWORK, OFFER_PORT))
        except:
            print_warning('Failed to send offer messages')
        sleep(DELAY_BETWEEN_OFFERS)


def send_offers_and_receive_players(join_socket):
    'Set up socket for sending offers and initiate phase 1 of server'
    with create_offer_socket() as offer_socket:
        join_port = join_socket.getsockname()[1]
        offer_sender = Process(
            target=send_offers,
            args=(offer_socket, join_port,))
        offer_sender.start()
        players = receive_players(join_socket)
        offer_sender.terminate()
    return players


def accept_players():
    'Set up socket for accepting clients and initiate phase 1 of server'
    with socket(AF_INET, SOCK_STREAM) as join_socket:
        join_socket.bind(('', 0))
        join_socket.listen(BACKLOG)
        join_socket.settimeout(DURATION)
        players = send_offers_and_receive_players(join_socket)
    return players


def server_round():
    'Method representing one server round'
    print('Sending out offer requests')
    players = accept_players()
    if not players:
        return
    q = Queue()
    send_start_message(players)
    play_game(players, q)
    post_game_analysis(players, q)


def main():
    'Main method for the server'
    print(f'Server started, listening on IP address {annotate_variable(HOST)}')
    while True:
        server_round()


if __name__ == "__main__":
    main()
