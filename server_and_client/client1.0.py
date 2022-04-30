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


def time_to_string(t):
    return f'{int(t // 3600)}:{int(t // 60)}:{int(t // 1)}'


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
    start_time = time.time()
    custom_key = get_custom_key()
    print(custom_key)
    settings = config.Config()
    local_player = player.Player(nickname="Hunnydrips", key=0, ip=0, Class='Tank')
    frame_counter = 0
    clock = pygame.time.Clock()
    clock.tick(60)
    camera_x = 0
    camera_y = 0
    running = True
    screen = pygame.display.set_mode((500, 500))
    while running:
        screen.fill((0, 0, 255))
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
            elif event.type == pygame.KEYDOWN:
                pressed = False
                # ------------------------------------------
                if event.key == pygame.K_RETURN and settings.chat_enabled:
                    settings.in_chat = not settings.in_chat
                    if not settings.in_chat:
                        if settings.chat_message:
                            while len(settings.chat_log) >= 5:
                                settings.chat_log = settings.chat_log[1:]
                            settings.chat_log.append(
                                f'({local_player.nickname}): {settings.chat_message} [{time_to_string(time.time() - start_time)}]')
                            settings.chat_message = ''
                    else:
                        packet = 'move0.0'
                elif settings.in_chat:
                    if len(settings.chat_message) < 45 and '~' >= event.unicode >= ' ':
                        settings.chat_message += event.unicode
                elif event.key == pygame.K_TAB:
                    settings.chat_enabled = not settings.chat_enabled
                elif event.key == pygame.K_y:
                    settings.camera_locked = not settings.camera_locked
                # ------------------------------------------
                elif event.key == pygame.K_w:
                    pressed = True
                    local_player.dir_y = -1
                elif event.key == pygame.K_s:
                    pressed = True
                    local_player.dir_y = 1
                elif event.key == pygame.K_a:
                    pressed = False
                    local_player.dir_x = -1
                elif event.key == pygame.K_d:
                    pressed = False
                    local_player.dir_x = 1
                # ------------------------------------------
                elif event.key == pygame.K_e:
                    packet = 'ability'
                elif event.key == pygame.K_u:
                    packet = 'upgrade'
                elif event.key == pygame.K_p:
                    packet = 'potion'
                elif event.key == pygame.K_q:
                    packet = 'pick-up'
                elif event.key == pygame.K_x:
                    packet = 'sell'
                elif pygame.K_1 <= event.key <= pygame.K_6:
                    if keys[pygame.K_i]:
                        packet = f'swap{int(event.unicode) - 1}'
                    else:
                        packet = f'pick{int(event.unicode) - 1}'
                # ------------------------------------------
                if pressed:
                    packet = f'move{local_player.dir_x}.{local_player.dir_y}'
            elif event.type == pygame.KEYUP:
                relised = False
                if event.key == pygame.K_w or event.key == pygame.K_s:
                    local_player.dir_y = 0
                    relised = True
                if event.key == pygame.K_a or event.key == pygame.K_d:
                    local_player.dir_x = 0
                    relised = True
                if relised:
                    packet = f'move{local_player.dir_x}.{local_player.dir_y}'
            elif event.type == pygame.MOUSEBUTTONDOWN and not settings.in_chat:
                if event.button == 1:
                    m_x, m_y = pygame.mouse.get_pos()
                    m_x += camera_x
                    m_y += camera_y
                    packet = f'attack{m_x},{m_y}'
                elif event.button == 4:
                    packet = 'scroll1'
                elif event.button == 5:
                    packet = 'scroll-1'

        if pygame.display.get_active():
            pygame.display.update()


if __name__ == '__main__':
    main()
