BUFFER_SIZE = 2048


def send_string(sock, message):
    """
    Encode the given string using utf-8,
    and sent it to the given socket.
    """
    return sock.send(message.encode())


def recv_string(sock):
    """
    Receive data from the given socket,
    and decode it using utf-8.
    """
    return sock.recv(BUFFER_SIZE).decode()
