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
screen = pygame.display.set_mode((500, 500))


def time_to_string(t):
    return f'{int(t // 3600)}:{int(t // 60)}:{int(t // 1)}'


# generates the custom key for encryption
def get_custom_key():
    public_key, private_key = encryption.generate_keys()
    print(public_key)
    client_socket.sendto(f'hi{public_key.n}.{public_key.e}'.encode(), server_ip)
    custom_key = client_socket.recvfrom(1024)[0]
    custom_key = encryption.decrypt_rsa(custom_key, private_key)

    print(custom_key)

    packet_log_in = 'log_inusername,password'
    packet_log_in = encryption.encrypt(msg=packet_log_in, key=custom_key)
    client_socket.sendto(packet_log_in.encode(), server_ip)
    log_in_answer = client_socket.recvfrom(1024)[0].decode()

    print(log_in_answer)
    log_in_answer = encryption.decrypt(msg=log_in_answer, key=custom_key)
    print(log_in_answer)
    log_in_data = log_in_answer[15:]
    x, y, Class, nick_name, health, gold, start_syn = log_in_data.split('.')
    x = int(x)
    y = int(y)
    health = int(health)
    local_player.x = x
    local_player.y = y
    local_player.health = health
    local_player.Class = Class
    local_player.nickname = nick_name
    local_player.gold = gold
    return custom_key, int(start_syn)


def recv(custom_key):
    msg = client_socket.recvfrom(1024)[0].decode()
    msg = encryption.decrypt(msg=msg, key=custom_key)
    if msg.startswith('loc'):
        msg = msg[3:]
        x, y = msg.split('.')
        local_player.x = int(x)
        local_player.y = int(y)


def update_player_direction_based_on_input(P: player.Player):
    keys = pygame.key.get_pressed()
    P.dir_x = keys[pygame.K_d] - keys[pygame.K_a]
    P.dir_y = keys[pygame.K_s] - keys[pygame.K_w]


def show_entities_and_their_particles(entity, cx: int, ch: int):
    entity.x -= cx
    entity.y -= ch
    if type(entity) == type(mob.Mob(x=0, y=0, lvl=0)):
        M_rect.center = entity.x, entity.y
        if entity.is_alive:
            if entity.is_melee:
                screen.blit(zombie_image, M_rect)
            else:
                screen.blit(mob_image, M_rect)
            show_mob_lvl(M=entity)
            show_mob_health(M=entity)
    else:
        P_rect.center = entity.x, entity.y
        if entity.Class == 'Mage':
            screen.blit(pygame.transform.flip(mage_img, entity.last_dir == -1, False), P_rect)
        elif entity.Class == 'Tank':
            screen.blit(pygame.transform.flip(tank_img, entity.last_dir == -1, False), P_rect)
        elif entity.Class == 'Scout':
            screen.blit(pygame.transform.flip(scout_img, entity.last_dir == -1, False), P_rect)
        show_player_health(P=entity)
        show_player_nickname(P=entity)
    entity.x += cx
    entity.y += ch
    for S in entity.projectiles:
        S.hit_box.x -= cx
        S.hit_box.y -= ch
        screen.blit(S.image, S.hit_box)
        S.hit_box.x += cx
        S.hit_box.y += ch


def show_mob_health(M: mob.Mob):
    pygame.draw.rect(screen, (0, 255, 0), ((M.x - 50, M.y - 75), (M.health // M.lvl, 10)))
    pygame.draw.rect(screen, (255, 0, 0), ((M.x - 50 + M.health // M.lvl, M.y - 75), (100 - M.health // M.lvl, 10)))


def show_ability_cool_down(P: player.Player, camera_x: int, camera_y: int):
    T = P.get_cd_left()
    if not P.is_ability_active:
        if T >= 10:
            pygame.draw.rect(screen, (40, 30, 240),
                             ((P.x - camera_x - 50, P.y - camera_y - 57), (100, 3)))
        else:
            T *= 10
            T = int(T)
            pygame.draw.rect(screen, (40, 160, 80),
                             ((P.x - camera_x - 50, P.y - camera_y - 57), (T, 3)))
    else:
        if P.Class == 'Tank':
            T *= 33
            T = int(T)
        elif P.Class == 'Scout':
            T *= 50
            T = int(T)
        pygame.draw.rect(screen, (40, 30, 240), ((P.x - camera_x - 50, P.y - camera_y - 57), (100 - T, 3)))


def show_player_health(P: player.Player):
    pygame.draw.rect(screen, (0, 255, 0), ((P.x - 50, P.y - 70), (P.health, 10)))
    pygame.draw.rect(screen, (255, 0, 0), ((P.x - 50 + P.health, P.y - 70), (100 - P.health, 10)))
    if P.income_dmg_multiplier == 0:
        pygame.draw.rect(screen, (255, 255, 0), ((P.x - 50, P.y - 70), (P.health, 10)))


def show_mob_lvl(M: mob.Mob):
    name = font.render(str(M.lvl), True, (0, 0, 0))
    name_rect = name.get_rect()
    name_rect.center = M.x, M.y
    name_rect.y -= 70
    name_rect.x -= 70
    screen.blit(name, name_rect)


def show_player_nickname(P: player.Player):
    name = font.render(P.nickname, True, (0, 0, 0))
    name_rect = name.get_rect()
    name_rect.center = P.x, P.y
    name_rect.y -= 90
    screen.blit(name, name_rect)


local_player = player.Player(nickname="Hunnydrips", key=0, ip=0, Class='Tank')
P_rect = pygame.Rect((0, 0), (66, 92))
M_rect = pygame.Rect((0, 0), (88, 120))

font = pygame.font.Font("freesansbold.ttf", 20)
font_gold = pygame.font.Font("freesansbold.ttf", 100)

gold_coin = pygame.image.load('../Assets/coins/gold.png')
silver_coin = pygame.image.load('../Assets/coins/silver.png')
bronze_coin = pygame.image.load('../Assets/coins/bronze.png')

gold_coin = pygame.transform.scale(gold_coin, (70, 70))
silver_coin = pygame.transform.scale(silver_coin, (70, 70))
bronze_coin = pygame.transform.scale(bronze_coin, (70, 70))

chat_box = pygame.image.load('../Assets/basics/chatBox.png')

chat_box = pygame.transform.scale(chat_box, (540, 30))

icon_bow = pygame.image.load('../Assets/icons/icon-bow.png')
icon_dagger = pygame.image.load('../Assets/icons/icon-dagger.png')
icon_snowball = pygame.image.load('../Assets/icons/icon-cumball.png')

icon_bow = pygame.transform.scale(icon_bow, (70, 70))
icon_dagger = pygame.transform.scale(icon_dagger, (70, 70))
icon_snowball = pygame.transform.scale(icon_snowball, (70, 70))

mob_image = pygame.image.load('../Assets/basics/mob.png')
zombie_image = pygame.image.load('../Assets/basics/zombie.png')
# classes sprites:
mage_img = pygame.image.load('../Assets/basics/Mage.png')
tank_img = pygame.image.load('../Assets/basics/Tank.png')
scout_img = pygame.image.load('../Assets/basics/Scout.png')

settings = config.Config()


def main():
    start_time = time.time()
    custom_key, start_syn = get_custom_key()
    print('start syn', start_syn)
    frame_counter = 0
    clock = pygame.time.Clock()
    clock.tick(60)
    camera_x = 0
    camera_y = 0
    running = True
    while running:
        screen.fill((255, 255, 255))
        show_entities_and_their_particles(local_player, camera_x, camera_y)
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            packet = False
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
                        packet = f'{start_syn}move0.0'
                elif settings.in_chat:
                    if len(settings.chat_message) < 45 and '~' >= event.unicode >= ' ':
                        settings.chat_message += event.unicode
                elif event.key == pygame.K_TAB:
                    settings.chat_enabled = not settings.chat_enabled
                elif event.key == pygame.K_y:
                    settings.camera_locked = not settings.camera_locked
                    print(settings.camera_locked)
                # ------------------------------------------
                elif event.key == pygame.K_w:
                    pressed = True
                    local_player.dir_y = -1
                elif event.key == pygame.K_s:
                    pressed = True
                    local_player.dir_y = 1
                elif event.key == pygame.K_a:
                    pressed = True
                    local_player.dir_x = -1
                elif event.key == pygame.K_d:
                    pressed = True
                    local_player.dir_x = 1
                # ------------------------------------------
                elif event.key == pygame.K_e:
                    packet = f'{start_syn}ability'
                elif event.key == pygame.K_u:
                    packet = f'{start_syn}upgrade'
                elif event.key == pygame.K_p:
                    packet = f'{start_syn}potion'
                elif event.key == pygame.K_q:
                    packet = f'{start_syn}pick-up'
                elif event.key == pygame.K_x:
                    packet = f'{start_syn}sell'
                elif pygame.K_1 <= event.key <= pygame.K_6:
                    if keys[pygame.K_i]:
                        packet = f'{start_syn}swap{int(event.unicode) - 1}'
                    else:
                        packet = f'{start_syn}pick{int(event.unicode) - 1}'
                # ------------------------------------------
                if pressed:
                    packet = f'{start_syn}move{local_player.dir_x}.{local_player.dir_y}'
            elif event.type == pygame.KEYUP:
                released = False
                if event.key == pygame.K_w or event.key == pygame.K_s:
                    local_player.dir_y = 0
                    released = True
                if event.key == pygame.K_a or event.key == pygame.K_d:
                    local_player.dir_x = 0
                    released = True
                if released:
                    packet = f'{start_syn}move{local_player.dir_x}.{local_player.dir_y}'
            elif event.type == pygame.MOUSEBUTTONDOWN and not settings.in_chat:
                if event.button == 1:
                    m_x, m_y = pygame.mouse.get_pos()
                    m_x += camera_x
                    m_y += camera_y
                    packet = f'{start_syn}attack{m_x}.{m_y}'
                elif event.button == 4:
                    packet = f'{start_syn}scroll1'
                elif event.button == 5:
                    packet = f'{start_syn}scroll-1'

            if packet:
                print(packet)
                packet = encryption.encrypt(msg=packet, key=custom_key)
                start_syn += 1
                if start_syn == 1000:
                    start_syn = 100
                client_socket.sendto(packet.encode(), server_ip)

        if settings.camera_locked:
            camera_x = local_player.x - screen.get_width() // 2
            camera_y = local_player.y - screen.get_height() // 2
        else:
            camera_x -= (keys[pygame.K_LEFT] - keys[pygame.K_RIGHT])
            camera_y += (keys[pygame.K_DOWN] - keys[pygame.K_UP])
        # show_background(x=camera_x, y=camera_y, img=map_img)
        # if pygame.display.get_active():
        pygame.display.update()


if __name__ == '__main__':
    main()
