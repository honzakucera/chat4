"""chatserver lib"""

from itertools import cycle
from Crypto.Cipher import AES
from Crypto.Hash import SHA256


def encrypt(message, key):
    """encrypt message"""
    cipher = AES.new(SHA256.new(key.encode()).digest(), AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(message.encode())
    encrypted = nonce+ciphertext+tag
    return encrypted


def decrypt(message, key):
    """dectypt message"""
    nonce = message[0:16]
    cipher = AES.new(SHA256.new(key.encode()).digest(), AES.MODE_EAX, nonce=nonce)
    ciphertext = message[16:-16]
    tag = message[-16:]
    decrypted = cipher.decrypt(ciphertext)
    try:
        cipher.verify(tag)
    except ValueError:
        return "<!> Key incorrect or message corrupted"
    return decrypted.decode()


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
