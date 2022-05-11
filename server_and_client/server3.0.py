import threading
import pygame
import socket
import time
import random
from Classes import player, item, dropped_item, mob

start_time = time.time()

pygame.init()

items_on_surface = []
P_rect = pygame.Rect((0, 0), (66, 92))
M_rect = pygame.Rect((0, 0), (88, 120))
udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_server_socket.bind(('0.0.0.0', 42069))
players = []
mobs = []

for i in range(1, 101):
    mobs.append(mob.Mob(random.randint(0, 40000), random.randint(0, 20000), i))


def time_to_string(t):
    return f'{int(t // 3600)}:{int(t // 60)}:{int(t // 1)}'


def receive():
    while True:
        data, ip = udp_server_socket.recvfrom(1024)
        data = data.decode()
        if data.startswith('hi'):
            print("new player connected")
            players.append(player.Player(nickname='a', ip=ip, key=0, Class='tmp'))  # change to database
            threading.Thread(target=receive, daemon=True).start()
        else:
            current_player = player.Player(nickname='Oni~Chan', ip=0, key=0, Class='tmp')
            for check_player in players:
                if check_player.socket_send == ip:
                    current_player = check_player
                    break
            if data.startswith('M'):
                print("player changed direction")
                print(data)
                x_dir, y_dir = data[1:].split('.')
                current_player.dir_x = int(x_dir)
                current_player.dir_y = int(y_dir)
            elif data.startswith('*'):
                nickname, symbol = data[1:].split('|')
                for player1 in players:
                    if player1.nickname == nickname:
                        if symbol == 'p':
                            player1.socket_particles = ip
                        elif symbol == 'm':
                            player1.socket_mobs = ip
                        elif symbol == 'o':
                            player1.socket_location = ip
                        elif symbol == 'c':
                            player1.socket_chat = ip
            elif data.startswith('s'):
                print('sign up received')
                nickname, username_hash, password_hash, Class = data[1:].split('.')
                try:
                    file = open(f"../Database/{username_hash}.txt", 'rb')
                    file.close()
                    udp_server_socket.sendto('sdenyaccess'.encode(), current_player.socket_send)
                except:
                    file = open(f"../Database/{username_hash}.txt", 'a+')
                    x, y, gold, health = 1000, 1000, 0, 100
                    inventory = "bow,1@False@False@False@False@False"
                    file.write(f'{nickname}\n{password_hash}\n{Class}\n{x}\n{y}\n{gold}\n{health}\n{inventory}')
                    file.close()
                    current_player.Class = Class
                    current_player.nickname = nickname
                    udp_server_socket.sendto('sallow'.encode(), current_player.socket_send)
                    packet_for_others = f'L{current_player.x}.{current_player.y}.{current_player.Class}' \
                                        f'.{current_player.nickname}.{current_player.health}'
                    for player1 in players:
                        if player1.Class != 'tmp':
                            packet = f"L{player1.x}.{player1.y}.{player1.Class}.{player1.nickname}.{player1.health}"
                            udp_server_socket.sendto(packet.encode(), current_player.socket_send)
                            udp_server_socket.sendto(packet_for_others.encode(), player1.socket_location)
                    current_player.username = username_hash

            elif data.startswith('l'):
                username_hash, password_hash = data[1:].split('.')
                print("login attempt")
                print(username_hash, password_hash)
                try:
                    file = open(f"../Database/{username_hash}.txt", 'r')
                    nickname, password_hash_in_db, Class, x, y, gold, health, inventory = file.read().split('\n')
                    file.close()
                    if password_hash_in_db == password_hash:
                        for player1 in players:
                            if player1.nickname == nickname:
                                raise Exception
                        current_player.Class = Class
                        current_player.nickname = nickname
                        current_player.x = int(x)
                        current_player.y = int(y)
                        current_player.username = username_hash
                        current_player.health = int(health)
                        current_player.gold = int(gold)
                        for i, itema in enumerate(inventory.split('@')):
                            if itema == "False":
                                current_player.inventory[i] = False
                            else:
                                current_player.inventory[i] = item.Item(itema.split(",")[0], int(itema.split(",")[1]))
                        udp_server_socket.sendto(
                            f"lallow{nickname}.{Class}.{x}.{y}.{gold}.{health}.{inventory}".encode(),
                            current_player.socket_send)
                        packet_for_others = f'L{current_player.x}.{current_player.y}.{current_player.Class}' \
                                            f'.{current_player.nickname}.{current_player.health}'
                        for player1 in players:
                            if player1.Class != 'tmp':
                                packet = f"L{player1.x}.{player1.y}.{player1.Class}.{player1.nickname}.{player1.health}"
                                udp_server_socket.sendto(packet.encode(), current_player.socket_send)
                                udp_server_socket.sendto(packet_for_others.encode(), player1.socket_location)
                    else:
                        raise Exception
                except:
                    udp_server_socket.sendto('ldenyaccess'.encode(), current_player.socket_send)
            elif data == "L":
                print("leaving")
                print(current_player.x, current_player.y)
                players.remove(current_player)
                if current_player.health == 0:
                    current_player.health = 50
                if current_player.Class != 'tmp':
                    for player1 in players:
                        if player1.Class != 'tmp':
                            packet = f'8{current_player.nickname}'
                            udp_server_socket.sendto(packet.encode(), player1.socket_location)
                    file = open(f'../Database/{current_player.username}.txt', 'r')
                    password = file.read().split('\n')[1]
                    file.close()
                    inventory = ''
                    for itemb in current_player.inventory:
                        if itemb:
                            inventory += f'{itemb.name},{itemb.lvl}'
                        else:
                            inventory += "False"
                        inventory += '@'
                    inventory = inventory[:-1]
                    file = open(f'../Database/{current_player.username}.txt', 'w')
                    file.write(
                        f'{current_player.nickname}\n{password}\n{current_player.Class}\n{current_player.x}'
                        f'\n{current_player.y}\n{current_player.gold}\n{current_player.health}\n{inventory}')
                    file.close()
                    print(
                        f'{current_player.nickname}\n{password}\n{current_player.Class}\n{current_player.x}'
                        f'\n{current_player.y}\n{current_player.gold}\n{current_player.health}\n{inventory}')
            elif data.startswith('A'):
                target_x, target_y = data[1:].split('.')
                print(target_x, target_y)
                current_player.attack(int(target_x), int(target_y))
            elif data.startswith('a'):
                if not current_player.is_ability_active:
                    current_player.use_ability()
            elif data.startswith('4'):
                dir_of_scroll = int(data[1:])
                current_player.picked += dir_of_scroll
                current_player.picked %= 6
            elif data.startswith('c'):
                msg = data
                msg += f' [{time_to_string(time.time() - start_time)}]'
                for player1 in players:
                    if player1.Class != 'tmp':
                        udp_server_socket.sendto(msg.encode(), player1.socket_chat)
            elif data.startswith('j'):
                current_player.picked = int(data[1:])
            elif data.startswith('b'):
                current_player.inventory[current_player.picked], current_player.inventory[int(data[1:])] = \
                    current_player.inventory[int(data[1:])], current_player.inventory[current_player.picked]


def move_players():
    while 1:
        for player1 in players:
            if player1.Class != 'tmp':
                player1.ability()
                if player1.move():
                    print('moved')
                    for player2 in players:
                        if player2.Class != 'tmp':
                            packet = f"L{player1.x}.{player1.y}.{player1.Class}.{player1.nickname}.{player1.health}"
                            if player1 in players:
                                print('1')
                                print(packet)
                                print('2')
                                udp_server_socket.sendto(packet.encode(), player2.socket_location)
                move_particles_for_entity(entity=player1)


#
def move_particles_for_entity(entity):
    for particle in entity.projectiles:
        if particle.move(entity.x, entity.y):
            packet = f'2{particle.x}|{particle.y}|{particle.angle}|{particle.name}|{particle.id_of_particle}'
            print(packet)
            for player1 in players:
                udp_server_socket.sendto(packet.encode(), player1.socket_particles)
            if particle.range <= 0 or (particle.hit and particle.speed != 1):
                packet = f'7{particle.x}|{particle.y}|{particle.angle}|{particle.name}|{particle.id_of_particle}'
                entity.projectiles.remove(particle)
                for player1 in players:
                    udp_server_socket.sendto(packet.encode(), player1.socket_particles)


def identify_par_dmg(Ps: list, Ms: list):
    while True:
        """
        gotaa have a thread for itself and the list should be globals
        :param Ps: A list of all the players that exist in the game
        :param Ms: A list of the mobs
        :return: new health for each entity
        """
        for M in Ms:
            for S in M.projectiles:
                for P in Ps:
                    P_rect.center = P.x, P.y
                    if P_rect.colliderect(S.hit_box) and not S.hit:
                        M.projectiles.remove(S)
                        S.hit = True
                        P.health -= int(10 * P.income_dmg_multiplier)
                        if P.health <= 0:
                            P.health = 0
                        packet = f"L{P.x}.{P.y}.{P.Class}.{P.nickname}.{P.health}"
                        for player1 in players:
                            udp_server_socket.sendto(packet.encode(), player1.socket_location)
        for P1 in Ps:
            for par in P1.projectiles:
                for M in Ms:
                    if M.is_alive:
                        M_rect.center = M.x, M.y
                        if M_rect.colliderect(par.hit_box) and not par.hit:
                            par.hit = True
                            M.health -= par.dmg
                            if M.health <= 0:
                                P1.gold += M.worth
                                M.death_time = time.time()
                                M.is_alive = False
                                items_on_surface.append(generate_drop(M.x, M.y, M.lvl))
                                packet = f'${M.lvl}'
                                for player1 in players:
                                    if player1.Class != 'tmp':
                                        udp_server_socket.sendto(packet.encode(), player1.socket_mobs)

                for P2 in Ps:
                    if P2.nickname != P1.nickname:
                        P2_rect = pygame.Rect((0, 0), (66, 92))
                        P2_rect.center = P2.x, P2.y
                        if P2_rect.colliderect(par.hit_box) and not par.hit:
                            par.hit = True
                            P2.health -= int(par.dmg * P2.income_dmg_multiplier)
                            if P2.health <= 0:
                                P2.health = 0
                            packet = f"L{P2.x}.{P2.y}.{P2.Class}.{P2.nickname}.{P2.health}"
                            for player1 in players:
                                udp_server_socket.sendto(packet.encode(), player1.socket_location)


def generate_drop(x, y, average):
    lvl = abs(random.randint(average - 11, average + 9)) + 1
    name = random.randint(0, 2)
    if name == 0:
        return dropped_item.Dropped_item(x, y, lvl, 'bow', time.time())
    elif name == 1:
        return dropped_item.Dropped_item(x, y, lvl, 'dagger', time.time())
    return dropped_item.Dropped_item(x, y, lvl, "cumball", time.time())


def move_mobs(mobs: list):
    while 1:
        for Mo in mobs:
            if Mo.move(players=players):
                packet = f'm{int(Mo.lvl)}|{int(Mo.x)}|{int(Mo.y)}|{int(Mo.health)}|{Mo.is_melee}'
                for player1 in players:
                    if player1.Class != 'tmp':
                        udp_server_socket.sendto(packet.encode(), player1.socket_mobs)


def main():
    threading.Thread(target=receive, daemon=True).start()
    # threading.Thread(target=move_players, daemon=True).start()
    threading.Thread(target=identify_par_dmg, daemon=True, args=(players, mobs,)).start()
    threading.Thread(target=move_mobs, daemon=True, args=(mobs,)).start()
    move_players()


if __name__ == '__main__':
    main()
