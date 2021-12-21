#!/usr/bin/env python3
"""chatserver client"""

import sys
from argparse import ArgumentParser
from select import select
from socket import AF_INET, SOCK_STREAM, socket
from time import time

from Crypto.Random.random import getrandbits

from chatlib import handshake, encrypt, decrypt


def main():
    """main"""

    parser = ArgumentParser()
    parser.add_argument('--server', default='chatserver')
    parser.add_argument('--port', type=int, default=7000)
    args = parser.parse_args()

    key = getrandbits(32)
    conn = socket(AF_INET, SOCK_STREAM)
    conn.connect((args.server, args.port))
    conn_key = handshake(conn, key)

    while True:
        sockets_list = [sys.stdin, conn]
        read_sockets, _, _ = select(sockets_list, [], [])
        for sock in read_sockets:
            if sock == conn:
                message = decrypt(sock.recv(2048), conn_key)
                if message:
                    print(message)
            elif sock == sys.stdin:
                message = sys.stdin.readline().strip()
                conn.send(encrypt(message, conn_key))
                print(f'<You> {message}')
            else:
                raise RuntimeError('invalid socket to be processed')

    conn.close()


if __name__ == '__main__':
    main()
