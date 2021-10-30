"""chatserver lib"""

from itertools import cycle


def xor(message, key):
    """encrypt message"""

    return ''.join(chr(ord(c) ^ ord(k)) for c, k in zip(message, cycle(key)))


class LCG:  # pylint: disable=too-few-public-methods
    """https://stackoverflow.com/a/9024521/8326867"""

    def __init__(self, seed=1):
        self.state = seed

    def random(self):
        """generate next random"""

        self.state = (1103515245 * self.state + 12345) % (2**31)
        return self.state


def handshake(conn, priv_key):
    """DH kex"""

    base = 524287
    modulus = 2147483647

    my_pubkey = pow(base, priv_key, modulus)

    conn.send(str(my_pubkey).encode())
    their_pubkey = int(conn.recv(2048).decode())

    conn_key = str(pow(their_pubkey, priv_key, modulus))
    print('DEBUG: priv_key %s conn_key %s' % (priv_key, conn_key))
    return conn_key
