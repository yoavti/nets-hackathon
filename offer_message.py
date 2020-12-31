from struct import pack, unpack
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEPORT, SO_BROADCAST


OFFER_PORT = 13117
FORMAT = '!IBH'
COOKIE = 0xfeedbeef
TYPE = 0x2


def create_offer_socket():
    offer_socket = socket(AF_INET, SOCK_DGRAM)
    offer_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
    offer_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    return offer_socket


def pack_offer(server_port):
    """
    Return a bytes object containing the given server port,
    along with the relevant cookie and type,
    packed according to the offer format.
    """
    return pack(FORMAT, COOKIE, TYPE, server_port)


def unpack_offer(offer):
    """
    Return the server port given in the message,
    which was unpacked according to the offer format,
    doing so only after checking that the cookie and type are correct.
    """
    try:
        magic_cookie, message_type, server_port = unpack(FORMAT, offer)
        return None if magic_cookie != COOKIE or message_type != TYPE else server_port
    except:
        return None
