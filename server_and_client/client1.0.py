import pygame
import socket
import time
import threading
import random
from Classes import dropped_item, player, mob, encryption, item, packet_builder

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.bind(('0.0.0.0', 123))
server_ip = ('127.0.0.1',42069)

if __name__ == '__main__':
    public_key, private_key = encryption.generate_keys()
    print(public_key)

    client_socket.sendto(f'hi{public_key.n}.{public_key.e}'.encode(), server_ip)
    custom_key = client_socket.recv(1024)
    custom_key = encryption.decrypt_rsa(custom_key, private_key)
    print(custom_key)