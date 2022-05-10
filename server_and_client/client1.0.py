import socket
import sys
import threading
from Classes import player, config, mob, item, particle
import pygame
import time

client_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_ip = ('127.0.0.1', 42069)

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
settings = config.Config()


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


def show_mob_health(m: mob.Mob):
    pygame.draw.rect(screen, (0, 255, 0), ((m.x - 50, m.y - 75), (m.health // m.lvl, 10)))
    pygame.draw.rect(screen, (255, 0, 0), ((m.x - 50 + m.health // m.lvl, m.y - 75), (100 - m.health // m.lvl, 10)))
    return


def show_mob_lvl(m: mob.Mob):
    name = font.render(str(m.lvl), True, (0, 0, 0))
    name_rect = name.get_rect()
    name_rect.center = m.x, m.y
    name_rect.y -= 70
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
            show_mob_lvl(m=entity)
            show_mob_health(m=entity)
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
        client_udp_socket.sendto(packet.encode(), server_ip)
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


def receive():
    while 1:
        data_from_server = client_udp_socket.recvfrom(1024)[0].decode()
        if data_from_server.startswith('L'):
            x, y = data_from_server[1:].split('.')
            local_player.x, local_player.y = int(x), int(y)
        elif data_from_server.startswith('o'):
            x, y, Class, nickname, health = data_from_server[1:].split('.')
            player2 = player.Player(nickname=nickname, Class=Class, ip=0, key=0)
            player2.x = int(x)
            player2.y = int(y)
            player2.health = int(health)
            local_player.other_players_list.append(player2)
        elif data_from_server.startswith('2'):
            print(data_from_server[1:])
            local_player.projectiles = []
            for particle1 in data_from_server[1:].split('@'):
                print(particle1)
                x, y, angle, name = particle1.split('|')
                local_player.projectiles.append(
                    particle.Particle(x=int(float(x)), y=int(float(y)), target_x=0, target_y=0, speed=0, range=0, dmg=0,
                                      name=name))
                local_player.projectiles[-1].angle = float(angle)
        elif data_from_server.startswith('7'):
            x, y, angle, name = data_from_server[1:].split('|')
            for par1 in local_player.projectiles:
                if par1.angle == float(angle):
                    local_player.projectiles.remove(par1)
        elif data_from_server.startswith('H'):
            pass
        elif data_from_server.startswith('G'):
            pass
        elif data_from_server.startswith('I'):
            pass
        elif data_from_server.startswith('C'):
            pass
        elif data_from_server.startswith('a'):
            local_player.is_ability_active = True
            local_player.last_time_used_ability = time.time()


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
    client_udp_socket.sendto(f's{nickname}.{username}.{password}.{classa}'.encode(), server_ip)
    data = client_udp_socket.recvfrom(1024)[0].decode()
    print(data)
    if data == "sallow":
        local_player.nickname = nickname
        local_player.Class = classa
    return data == "sallow"


def login(username: str, password: str):
    client_udp_socket.sendto(f'l{username}.{password}'.encode(), server_ip)
    data = client_udp_socket.recvfrom(1024)[0].decode()
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
    client_udp_socket.sendto("hi".encode(), server_ip)
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
                pygame.quit()
                client_udp_socket.sendto("L".encode(), server_ip)
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
        cl.tick(60)
        pygame.display.update()
    threading.Thread(target=receive, daemon=True).start()
    threading.Thread(target=receive, daemon=True).start()
    threading.Thread(target=receive, daemon=True).start()
    threading.Thread(target=receive, daemon=True).start()
    threading.Thread(target=receive, daemon=True).start()
    threading.Thread(target=receive, daemon=True).start()
    threading.Thread(target=receive, daemon=True).start()
    running = True
    while running:
        screen.fill('red')
        movement()
        settings.camera_x, settings.camera_y = \
            local_player.x - screen.get_width() // 2, local_player.y - screen.get_height() // 2
        show_background(camera_x=settings.camera_x, camera_y=settings.camera_y)
        show_ability_cool_down(local_player, settings.camera_x, settings.camera_y)
        show_inventory(local_player)
        show_entities_and_their_particles(camera_x=settings.camera_x, camera_y=settings.camera_y, entity=local_player)
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                client_udp_socket.sendto("L".encode(), server_ip)
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                packet = f'A{mx + settings.camera_x}.{my + settings.camera_y}'
                print(packet)
                client_udp_socket.sendto(packet.encode(), server_ip)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    packet = 'a'
                    client_udp_socket.sendto(packet.encode(), server_ip)
        for p in local_player.other_players_list:
            show_entities_and_their_particles(p, settings.camera_x, settings.camera_y)
        local_player.other_players_list = []
        cl.tick(60)
        pygame.display.update()


if __name__ == '__main__':
    main()
