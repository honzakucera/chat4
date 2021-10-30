#!/usr/bin/env python3
"""chatserver server"""

import logging
from argparse import ArgumentParser
from socket import AF_INET, SOCK_STREAM, socket, SOL_SOCKET, SO_REUSEADDR
from threading import Thread

from chatlib import handshake, LCG, xor


list_of_clients = []


def client_thread(conn, addr, key):
    """client thread"""

    print(f'{addr[0]} connected')
    conn_key = handshake(conn, key)
    list_of_clients.append((conn, conn_key))

    conn.send(xor('Welcome to this chatroom!', conn_key).encode())

    while True:
        try:
            message = xor(conn.recv(2048).decode(), conn_key)
            if message:
                broadcast(f'<{addr[0]}> {message}', conn)
            else:
                break
        except Exception as exc:  # noqa: E722 pylint: disable=broad-except
            logging.error('cannot handle message: %s', exc)
            break

    conn.close()
    remove((conn, conn_key))


def broadcast(message, from_conn):
    """send message to all clients except the original sender"""

    for client, client_key in list_of_clients:
        if client != from_conn:
            try:
                client.send(xor(message, client_key).encode())
            except Exception as exc:  # noqa: E722 pylint: disable=broad-except
                logging.error('cannot broadcast message: %s', exc)
                client.close()
                remove((client, client_key))


def remove(conn_tuple):
    """remove dead client"""

    if conn_tuple in list_of_clients:
        list_of_clients.remove(conn_tuple)


def main():
    """main"""

    parser = ArgumentParser()
    parser.add_argument('--bindaddr', default='')
    parser.add_argument('--port', type=int, default=7000)
    args = parser.parse_args()

    key = LCG().random()
    server = socket(AF_INET, SOCK_STREAM)
    server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server.bind((args.bindaddr, args.port))
    server.listen(100)

    while True:
        conn, addr = server.accept()
        Thread(target=client_thread, args=(conn, addr, key)).start()

    for conn in list_of_clients:
        conn.close()
    server.close()


if __name__ == '__main__':
    main()
