from struct import pack, unpack


FORMAT = 'ich'
COOKIE = 0xfeedbeef
TYPE = 2


def pack_offer(server_port):
    return pack(FORMAT, COOKIE, TYPE, server_port)


def unpack_offer(offer):
    magic_cookie, message_type, server_port = unpack(FORMAT, offer)
    return None if magic_cookie != COOKIE or message_type != TYPE else server_port
