import pygame
import socket
import time
import threading
import random
from Classes import dropped_item, player, mob, encryption, item, packet_builder, config

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.bind(('0.0.0.0', 123))
server_ip = ('127.0.0.1', 42069)

pygame.init()



# generates the custom key for encryption
def get_custom_key():
    public_key, private_key = encryption.generate_keys()
    print(public_key)
    client_socket.sendto(f'hi{public_key.n}.{public_key.e}'.encode(), server_ip)
    custom_key = client_socket.recv(1024)
    custom_key = encryption.decrypt_rsa(custom_key, private_key)
    return custom_key


def update_player_direction_based_on_input(P: player.Player):
    keys = pygame.key.get_pressed()
    P.dir_x = keys[pygame.K_d] - keys[pygame.K_a]
    P.dir_y = keys[pygame.K_s] - keys[pygame.K_w]


def main():
    custom_key = get_custom_key()
    print(custom_key)
    settings = config.Config()
    client = player.Player(nickname="Hunnydrips", key=0, ip=0, Class='Tank')
    frame_counter = 0
    clock = pygame.time.Clock()
    clock.tick(60)
    camera_x = 0
    camera_y = 0
    running = True
    screen = pygame.display.set_mode((500, 500))
    while running:
        screen.fill((0, 0, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
        if pygame.display.get_active():
            pygame.display.update()


if __name__ == '__main__':
    main()

