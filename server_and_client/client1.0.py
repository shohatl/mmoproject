import math
import socket
import sys
import threading
import time

import pygame

from Classes import player, config, mob, item, particle, dropped_item

clock = pygame.time.Clock()

client_udp_socket_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_udp_socket_for_particles = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_udp_socket_for_mobs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_udp_socket_for_players = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_udp_socket_for_chat = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
settings = config.Config()
settings.server_ip = ('127.0.0.1', 42069)
players = []

pygame.init()
left_side_map = pygame.image.load('../Assets/basics/ground2.jpg')
right_side_map = pygame.image.load('../Assets/basics/ground2.jpg')
screen = pygame.display.set_mode((1500, 800))
local_player = player.Player('lidor', 0, 12345, 'Tank')

P_rect = pygame.Rect((0, 0), (66, 92))
M_rect = pygame.Rect((0, 0), (88, 120))
items_on_surface = []

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


class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str):
        self.rect = pygame.Rect((x, y), (width, height))
        self.is_pressed = False
        self.text = text

    def check_pressed(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()) \
                and pygame.mouse.get_pressed()[0] == 1 and not self.is_pressed:
            self.is_pressed = True
            return True
        if pygame.mouse.get_pressed()[0] == 0:
            self.is_pressed = False
        return False

    def reset(self):
        self.is_pressed = False

    def show(self):
        if self.is_pressed:
            pygame.draw.rect(screen, (100, 100, 100), self.rect)
        else:
            pygame.draw.rect(screen, (200, 200, 200), self.rect)
        txt = font.render(self.text, True, (0, 0, 0))
        r = txt.get_rect()
        r.center = self.rect.center
        screen.blit(txt, r)


class TextField:
    def __init__(self, x: int, y: int, width: int, height: int, text: str):
        self.rect = pygame.Rect((x, y), (width, height))
        self.is_pressed = False
        self.text = text
        self.current_text = text
        self.last_deleted = 0

    def check_pressed(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0] == 1:
            self.is_pressed = True
            self.current_text = ""

    def get_input(self):
        if self.is_pressed:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if ('Z' >= event.unicode >= '0' or 'z' >= event.unicode >= 'a') and len(self.current_text) <= 12:
                        self.current_text += event.unicode
            keys = pygame.key.get_pressed()
            if keys[pygame.K_BACKSPACE] and keys[pygame.K_LCTRL]:
                self.current_text = ''
            if keys[pygame.K_BACKSPACE] and self.current_text and time.time() - self.last_deleted > 0.1:
                self.last_deleted = time.time()
                self.current_text = self.current_text[:-1]

    def reset(self):
        self.is_pressed = False

    def show(self):
        if self.is_pressed:
            pygame.draw.rect(screen, (100, 100, 100), self.rect)
        else:
            pygame.draw.rect(screen, (200, 200, 200), self.rect)
        txt = font.render(self.current_text, True, (0, 0, 0))
        r = txt.get_rect()
        r.center = self.rect.center
        screen.blit(txt, r)


class RadioButton:
    def __init__(self, x: int, y: int, width: int, height: int, text: str):
        self.rect = pygame.Rect((x, y), (width, height))
        self.is_pressed = False
        self.text = text

    def check_pressed(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0] == 1:
            self.is_pressed = True

    def reset(self):
        self.is_pressed = False

    def show(self):
        if self.is_pressed:
            pygame.draw.rect(screen, (100, 100, 100), self.rect)
        else:
            pygame.draw.rect(screen, (200, 200, 200), self.rect)
        txt = font.render(self.text, True, (0, 0, 0))
        r = txt.get_rect()
        r.center = self.rect.center
        screen.blit(txt, r)


def show_player_health(p: player.Player, camera_x, camera_y):
    pygame.draw.rect(screen, (0, 255, 0), ((p.x - 50 - camera_x, p.y - 70 - camera_y), (p.health, 10)))
    pygame.draw.rect(screen, (255, 0, 0), ((p.x - 50 - camera_x + p.health, p.y - 70 - camera_y), (100 - p.health, 10)))
    if p.income_dmg_multiplier == 0:
        pygame.draw.rect(screen, (255, 255, 0), ((p.x - 50 - camera_x, p.y - 70 - camera_y), (p.health, 10)))
    return


def show_mob_health(m: mob.Mob, camera_x: int, camera_y: int):
    pygame.draw.rect(screen, (0, 255, 0), ((m.x - 50 - camera_x, m.y - 75 - camera_y), (m.health // m.lvl, 10)))
    pygame.draw.rect(screen, (255, 0, 0),
                     ((m.x - 50 - camera_x + m.health // m.lvl, m.y - 75 - camera_y), (100 - m.health // m.lvl, 10)))
    return


def show_mob_lvl(m: mob.Mob, camera_x: int, camera_y: int):
    name = font.render(str(m.lvl), True, (0, 0, 0))
    name_rect = name.get_rect()
    name_rect.center = m.x, m.y
    name_rect.y -= 70
    name_rect.x -= camera_x
    name_rect.y -= camera_y
    name_rect.x -= 70
    screen.blit(name, name_rect)
    return


def show_player_nickname(p: player.Player, camera_x, camera_y):
    name = font.render(p.nickname, True, (0, 0, 0))
    name_rect = name.get_rect()
    name_rect.center = p.x - camera_x, p.y - camera_y
    name_rect.y -= 90
    screen.blit(name, name_rect)
    return


def show_entities_and_their_particles(entity, camera_x: int, camera_y: int):
    entity_x = entity.x - camera_x
    entity_y = entity.y - camera_y
    if isinstance(entity, mob.Mob):
        M_rect.center = entity_x, entity_y
        if entity.is_alive:
            if entity.is_melee:
                screen.blit(zombie_image, M_rect)
            else:
                screen.blit(mob_image, M_rect)
            show_mob_lvl(m=entity, camera_x=camera_x, camera_y=camera_y)
            show_mob_health(m=entity, camera_x=camera_x, camera_y=camera_y)
    else:
        P_rect.center = entity_x, entity_y
        if entity.Class == 'Mage':
            screen.blit(pygame.transform.flip(mage_img, entity.last_dir == -1, False), P_rect)
        elif entity.Class == 'Tank':
            screen.blit(pygame.transform.flip(tank_img, entity.last_dir == -1, False), P_rect)
        elif entity.Class == 'Scout':
            screen.blit(pygame.transform.flip(scout_img, entity.last_dir == -1, False), P_rect)
        show_player_health(p=entity, camera_x=camera_x, camera_y=camera_y)
        show_player_nickname(p=entity, camera_x=camera_x, camera_y=camera_y)
    for S in entity.projectiles:
        S.image = pygame.image.load(f'../Assets/weapons/{S.name}.png')
        S.image = pygame.transform.rotate(S.image, S.angle)
        S.hit_box = S.image.get_rect()
        S.hit_box.center = S.x, S.y
        S.hit_box.x -= camera_x
        S.hit_box.y -= camera_y
        screen.blit(S.image, S.hit_box)
        S.hit_box.x += camera_x
        S.hit_box.y += camera_y
    return


def movement():
    keys = pygame.key.get_pressed()
    current_x_dir = keys[pygame.K_d] - keys[pygame.K_a]
    current_y_dir = keys[pygame.K_s] - keys[pygame.K_w]
    if current_x_dir != local_player.dir_x or current_y_dir != local_player.dir_y:
        local_player.dir_y = current_y_dir
        local_player.dir_x = current_x_dir
        packet = f'M{local_player.dir_x}.{local_player.dir_y}'
        client_udp_socket_send.sendto(packet.encode(), settings.server_ip)
    return


def show_ability_cool_down(p: player.Player, camera_x: int, camera_y: int):
    T = p.get_cd_left()
    if not p.is_ability_active:
        if T >= 10:
            pygame.draw.rect(screen, (40, 30, 240),
                             ((p.x - camera_x - 50, p.y - camera_y - 57), (100, 3)))
        else:
            T *= 10
            T = int(T)
            pygame.draw.rect(screen, (40, 160, 80),
                             ((p.x - camera_x - 50, p.y - camera_y - 57), (T, 3)))
    else:
        if p.Class == 'Tank':
            T *= 33
            T = int(T)
        elif p.Class == 'Scout':
            T *= 50
            T = int(T)
        if T >= 100:
            local_player.is_ability_active = False
        pygame.draw.rect(screen, (40, 30, 240), ((p.x - camera_x - 50, p.y - camera_y - 57), (100 - T, 3)))


def receive(sock: socket.socket):
    while 1:
        clock.tick(30)
        data_from_server = sock.recvfrom(1024)[0].decode()
        print(data_from_server)
        if data_from_server.startswith('L'):
            x, y, Class, nickname, health = data_from_server[1:].split('.')
            flag = True
            for player1 in players:
                if player1.nickname == nickname:
                    player1.x, player1.y, player1.health = int(x), int(y), int(health)
                    flag = False
            if flag:
                player2 = player.Player(nickname=nickname, Class=Class, ip=0, key=0)
                player2.x, player2.y, player2.health = int(x), int(y), int(health)
                players.append(player2)
        elif data_from_server.startswith('8'):
            nickname = data_from_server[1:]
            print(nickname)
            for player1 in players:
                if player1.nickname == nickname:
                    players.remove(player1)
                    break
        elif data_from_server.startswith('2'):
            print("Obtained particle!")
            x, y, angle, name, id_of_par, dmg, range, speed, nickname = data_from_server[1:].split('|')
            par = particle.Particle(x=int(float(x)), y=int(float(y)), target_x=0, target_y=0, speed=float(speed),
                                    range=float(range),
                                    dmg=float(dmg),
                                    name=name)
            par.id_of_particle = int(id_of_par)
            par.angle = float(angle)
            par.angle /= -180 / math.pi
            par.velocity_x = float(par.speed * math.cos(par.angle))
            par.velocity_y = float(par.speed * math.sin(par.angle))
            par.angle *= -180 / math.pi
            flag = True
            for player1 in players:
                if player1.nickname == nickname:
                    flag = False
                    player1.projectiles.append(par)
                    break
            if flag:
                players[0].projectiles.append(par)
        elif data_from_server.startswith('7'):
            id_of_par = data_from_server[1:]
            for player1 in players:
                for par1 in player1.projectiles:
                    if int(par1.id_of_particle) == int(id_of_par):
                        player1.projectiles.remove(par1)
        elif data_from_server.startswith('c'):
            settings.chat_log.append(data_from_server[1:])
            if len(settings.chat_log) > 5:
                settings.chat_log = settings.chat_log[1:]
        elif data_from_server.startswith('a'):
            local_player.is_ability_active = True
            local_player.last_time_used_ability = time.time()
        elif data_from_server.startswith('m'):
            print("Received dropping packet")
            lvl, x, y, health, is_melee = data_from_server[1:].split('|')
            if is_melee == 'False':
                is_melee = False
            else:
                is_melee = True
            flag = False
            for i, m in enumerate(players[0].mobs_on_screen):
                if m.lvl == int(lvl):
                    flag = True
                    players[0].mobs_on_screen[i].x = int(x)
                    players[0].mobs_on_screen[i].y = int(y)
                    players[0].mobs_on_screen[i].health = int(health)
            if not flag:
                players[0].mobs_on_screen.append(mob.Mob(int(x), int(y), int(lvl)))
                players[0].mobs_on_screen[-1].is_melee = is_melee
        elif data_from_server.startswith('$'):
            lvl, x, y, name = data_from_server[1:].split("|")
            D_item = dropped_item.Dropped_item(x=int(x), y=int(y), lvl=0, name=name, time_dropped=time.time())
            items_on_surface.append(D_item)
            for m in players[0].mobs_on_screen:
                if m.lvl == int(lvl):
                    players[0].mobs_on_screen.remove(m)
                    break
        elif data_from_server.startswith('G'):
            players[0].gold = int(data_from_server[1:])
        elif data_from_server.startswith('I'):
            print(data_from_server)
            for i, itemA in enumerate(data_from_server[1:].split('@')):
                if itemA == "False":
                    players[0].inventory[i] = False
                else:
                    players[0].inventory[i] = item.Item(itemA.split(",")[0], int(itemA.split(",")[1]))
        elif data_from_server.startswith('W'):
            for itemD in items_on_surface:
                if itemD.id == int(data_from_server[1:]):
                    items_on_surface.remove(itemD)


def show_background(camera_x: int, camera_y: int):
    if camera_x < left_side_map.get_width() + screen.get_width():
        screen.blit(left_side_map, (0, 0), ((camera_x, camera_y), (screen.get_size())))
        if camera_x > left_side_map.get_width() - screen.get_width():
            screen.blit(right_side_map, (left_side_map.get_width() - camera_x, 0), ((0, camera_y), (screen.get_size())))
    if camera_x > left_side_map.get_width() - screen.get_width():
        if camera_x > left_side_map.get_width() + screen.get_width():
            screen.blit(right_side_map, (0, 0), ((camera_x - left_side_map.get_width(), camera_y), (screen.get_size())))
    return


def sign_up(nickname: str, username: str, password: str, classa: str):
    client_udp_socket_send.sendto(f's{nickname}.{username}.{password}.{classa}'.encode(), settings.server_ip)
    data, ip = client_udp_socket_send.recvfrom(1024)
    data = data.decode()
    settings.server_ip = ip
    print(data)
    if data == "sallow":
        local_player.nickname = nickname
        local_player.Class = classa
    return data == "sallow"


def login(username: str, password: str):
    client_udp_socket_send.sendto(f'l{username}.{password}'.encode(), settings.server_ip)
    data, ip = client_udp_socket_send.recvfrom(1024)
    data = data.decode()
    settings.server_ip = ip
    print(data)
    if data.startswith("lallow"):
        nickname, Class, x, y, gold, health, inventory = data[6:].split('.')
        local_player.x = int(x)
        local_player.y = int(y)
        print(x, y)
        local_player.nickname = nickname
        local_player.Class = Class
        local_player.gold = int(gold)
        local_player.health = int(health)
        for i, itema in enumerate(inventory.split('@')):
            if itema == "False":
                local_player.inventory[i] = False
            else:
                local_player.inventory[i] = item.Item(itema.split(",")[0], int(itema.split(",")[1]))
        return True
    return False


def show_gold(gold: int):
    screen.blit(gold_coin, (35, screen.get_height() - 130))
    screen.blit(silver_coin, (0, screen.get_height() - 70))
    screen.blit(bronze_coin, (70, screen.get_height() - 70))
    to_add = ''
    if gold >= 1000000000:
        gold = int(gold / 100000000)
        gold /= 10.0
        to_add = 'T'
    elif gold >= 1000000:
        gold = int(gold / 100000)
        gold /= 10.0
        to_add = 'M'
    elif gold >= 1000:
        gold = int(gold / 100)
        gold /= 10
        to_add = 'K'
    toShow = font_gold.render(str(gold) + to_add, True, (255, 215, 0))
    screen.blit(toShow, (150, screen.get_height() - 110))
    return


def show_inventory(p: player.Player):
    slot_rect = pygame.Rect((screen.get_size()[0] - 490, screen.get_size()[1] - 90), (90, 90))
    in_hand_x, in_hand_y = 0, 0
    for i, I in enumerate(p.inventory):
        pygame.draw.rect(screen, (100, 100, 100), slot_rect, 10)
        if i == p.picked:
            in_hand_x = slot_rect.x
            in_hand_y = slot_rect.y
        if I:
            slot_rect.x += 10
            slot_rect.y += 10
            if I.name == 'bow':
                screen.blit(icon_bow, slot_rect)
            elif I.name == 'dagger':
                screen.blit(icon_dagger, slot_rect)
            else:
                screen.blit(icon_snowball, slot_rect)
            screen.blit(font.render(str(I.lvl), True, (255, 255, 255)), slot_rect)
            slot_rect.x -= 10
            slot_rect.y -= 10
        slot_rect.x += 80
    pygame.draw.rect(screen, (255, 255, 255), ((in_hand_x, in_hand_y), (90, 90)), 10)
    return


def main():
    client_udp_socket_send.sendto("hi".encode(), settings.server_ip)
    login_image = pygame.image.load("../Assets/basics/loginBackground.png")
    mode = Button(x=300, y=100, height=30, width=200, text="Login")
    cl = pygame.time.Clock()
    radio_buttons = []
    send_button = Button(400, 700, 150, 200, "Send")
    text_fields = [TextField(100, 500, 150, 50, 'Username'), TextField(300, 500, 150, 50, 'Password')]
    send_flag = True
    while send_flag:
        screen.blit(login_image, (0, 0))
        mode.show()
        send_button.show()
        if send_button.check_pressed():
            flag = True
            for text_field in text_fields:
                if text_field.text == text_field.current_text or text_field.current_text == "":
                    flag = False
            if flag:
                if mode.text == "Login":
                    if login(username=text_fields[0].current_text, password=text_fields[1].current_text):
                        send_flag = False
                else:
                    Class = ""
                    for radio_button in radio_buttons:
                        if radio_button.is_pressed:
                            Class = radio_button.text
                    if sign_up(username=text_fields[0].current_text, password=text_fields[1].current_text, classa=Class,
                               nickname=text_fields[2].current_text):
                        send_flag = False
        for text_field in text_fields:
            text_field.check_pressed()
            text_field.get_input()
            text_field.show()
            if text_field.is_pressed:
                for text_field2 in text_fields:
                    if text_field2.text != text_field.text:
                        text_field2.reset()
        for radio_button in radio_buttons:
            radio_button.show()
            radio_button.check_pressed()
            if radio_button.is_pressed:
                for radio_button2 in radio_buttons:
                    if radio_button2.text != radio_button.text:
                        radio_button2.reset()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                print("I am here")
                pygame.quit()
                client_udp_socket_send.sendto("L".encode(), settings.server_ip)
                sys.exit()
        if mode.check_pressed():
            print('pressed')
            if mode.text == 'Login':
                mode.text = 'Sign Up'
                radio_buttons = [RadioButton(100, 300, 100, 50, "Scout"), RadioButton(300, 300, 100, 50, "Mage"),
                                 RadioButton(500, 300, 100, 50, "Tank")]
                text_fields = [TextField(100, 500, 150, 50, 'Username'), TextField(300, 500, 150, 50, 'Password'),
                               TextField(500, 500, 150, 50, 'Nickname')]
                radio_buttons[0].is_pressed = True
            else:
                mode.text = 'Login'
                radio_buttons = []
                text_fields = [TextField(100, 500, 150, 50, 'Username'), TextField(300, 500, 150, 50, 'Password')]
        cl.tick(30)
        pygame.display.update()
    players.append(local_player)

    for i in range(5):
        packet = f'*{local_player.nickname}|p'
        client_udp_socket_for_particles.sendto(packet.encode(), settings.server_ip)
        packet = f'*{local_player.nickname}|o'
        client_udp_socket_for_players.sendto(packet.encode(), settings.server_ip)
        packet = f'*{local_player.nickname}|c'
        client_udp_socket_for_chat.sendto(packet.encode(), settings.server_ip)
        packet = f'*{local_player.nickname}|m'
        client_udp_socket_for_mobs.sendto(packet.encode(), settings.server_ip)

    threading.Thread(target=receive, daemon=True, args=(client_udp_socket_send,)).start()
    threading.Thread(target=receive, daemon=True, args=(client_udp_socket_for_players,)).start()
    threading.Thread(target=receive, daemon=True, args=(client_udp_socket_for_chat,)).start()
    threading.Thread(target=receive, daemon=True, args=(client_udp_socket_for_mobs,)).start()
    threading.Thread(target=receive, daemon=True, args=(client_udp_socket_for_particles,)).start()
    running = True
    frame = 0
    while running:
        frame += 1
        frame %= 60
        screen.fill('red')
        keys = pygame.key.get_pressed()
        if not settings.in_chat:
            movement()
        settings.camera_x, settings.camera_y = \
            players[0].x - screen.get_width() // 2, players[0].y - screen.get_height() // 2

        show_background(camera_x=settings.camera_x, camera_y=settings.camera_y)
        show_ability_cool_down(players[0], settings.camera_x, settings.camera_y)
        show_inventory(players[0])
        # ------------------------------ display chat messages
        if settings.chat_enabled:
            height_of_msg = 10
            for msg in settings.chat_log:
                screen.blit(font.render(msg, True, (255, 255, 255)), (20, height_of_msg))
                height_of_msg += 30
        # ------------------------------------

        # ------------------------------------- show the typed message
        if settings.in_chat:
            if keys[pygame.K_BACKSPACE] and keys[pygame.K_LCTRL]:
                settings.chat_message = ''
            if keys[pygame.K_BACKSPACE] and settings.chat_message and not frame % 4:
                settings.chat_message = settings.chat_message[:-1]
            screen.blit(chat_box, (10, 200))
            blinking_shit = ''
            if frame < 30:
                blinking_shit = '|'
            screen.blit(font.render(settings.chat_message + blinking_shit, True, (255, 255, 255)), (13, 205))
        if players[0].health == 0:
            client_udp_socket_send.sendto("L".encode(), settings.server_ip)
            pygame.quit()
            sys.exit()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                client_udp_socket_send.sendto("L".encode(), settings.server_ip)
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = pygame.mouse.get_pos()
                    packet = f'A{mx + settings.camera_x}.{my + settings.camera_y}'
                    print(packet)
                    client_udp_socket_send.sendto(packet.encode(), settings.server_ip)
                elif event.button == 4:
                    players[0].picked += 1
                    players[0].picked %= 6
                    packet = '41'
                    print(players[0].picked, 'new slot')
                    client_udp_socket_send.sendto(packet.encode(), settings.server_ip)
                elif event.button == 5:
                    players[0].picked -= 1
                    players[0].picked %= 6
                    print(players[0].picked, 'new slot')
                    packet = '4-1'
                    client_udp_socket_send.sendto(packet.encode(), settings.server_ip)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and settings.chat_enabled:
                    settings.in_chat = not settings.in_chat
                    if not settings.in_chat:
                        if settings.chat_message:
                            packet = f'c({players[0].nickname}): {settings.chat_message}'
                            settings.chat_message = ''
                            client_udp_socket_send.sendto(packet.encode(), settings.server_ip)
                    else:
                        client_udp_socket_send.sendto('M0.0'.encode(), settings.server_ip)
                elif settings.in_chat:
                    if len(settings.chat_message) < 45 and '~' >= event.unicode >= ' ':
                        settings.chat_message += event.unicode
                elif event.key == pygame.K_u:
                    if players[0].gold >= 1000:
                        client_udp_socket_send.sendto('U'.encode(), settings.server_ip)
                        print("Sent heal packet")
                elif event.key == pygame.K_n:
                    packet = 'R'
                    client_udp_socket_send.sendto(packet.encode(), settings.server_ip)
                elif event.key == pygame.K_m:
                    packet = 'b'
                    client_udp_socket_send.sendto(packet.encode(), settings.server_ip)
                    print("Sent item removal request")
                elif event.key == pygame.K_TAB:
                    settings.chat_enabled = not settings.chat_enabled
                elif event.key == pygame.K_e:
                    packet = 'a'
                    client_udp_socket_send.sendto(packet.encode(), settings.server_ip)
                elif pygame.K_1 <= event.key <= pygame.K_6:
                    players[0].picked = int(event.unicode) - 1
                    packet = f'j{int(event.unicode) - 1}'
                    client_udp_socket_send.sendto(packet.encode(), settings.server_ip)
        for D_item in items_on_surface:
            screen.blit(D_item.image, (D_item.x - settings.camera_x - 35, D_item.y - settings.camera_y - 35))
            if time.time() - D_item.time_dropped > 7:
                items_on_surface.remove(D_item)
        for p in players:
            show_entities_and_their_particles(entity=p, camera_x=settings.camera_x, camera_y=settings.camera_y)
            for par in p.projectiles:
                if par.range <= 0:
                    p.projectiles.remove(par)
                par.move(entity=p)
        for m in players[0].mobs_on_screen:
            show_entities_and_their_particles(entity=m, camera_x=settings.camera_x, camera_y=settings.camera_y)
        show_gold(gold=players[0].gold)
        pygame.display.update()
        clock.tick(30)


if __name__ == '__main__':
    main()
