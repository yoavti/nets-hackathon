from struct import pack, unpack


FORMAT = 'IBH'
COOKIE = 0xfeedbeef
TYPE = 0x2


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
