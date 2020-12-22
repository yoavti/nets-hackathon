BUFFER_SIZE = 2048
ENCODING_FORMAT = 'utf-8'


def send_string(sock, message):
    return sock.send(message.encode(ENCODING_FORMAT))


def recv_string(sock):
    return sock.recv(BUFFER_SIZE).decode(ENCODING_FORMAT)
