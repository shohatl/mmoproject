import random
import socket
import threading
import time

import pygame

from Classes import player, item, dropped_item, mob

start_time = time.time()
clock = pygame.time.Clock()
pygame.init()

P_rect = pygame.Rect((0, 0), (66, 92))
M_rect = pygame.Rect((0, 0), (88, 120))
login_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
login_server_socket.bind(('0.0.0.0', 42069))
players = []
mobs = []
items_on_surface = []

for i in range(1, 101):
    mobs.append(mob.Mob(random.randint(0, 40000), random.randint(0, 20000), i))

mobs[0].x = 100
mobs[0].y = 100
mobs[0].home_x = 100
mobs[0].home_y = 100


def time_to_string(t):
    return f'{int(t // 3600)}:{int(t // 60)}:{int(t // 1)}'


def receive(udp_server_socket: socket.socket):
    while True:
        if udp_server_socket == login_server_socket:
            print('login socket')
        data, ip = udp_server_socket.recvfrom(1024)
        data = data.decode()
        if data.startswith('hi'):
            print("new player connected")
            new_player = player.Player(nickname='', ip=ip, key=0, Class='tmp')
            players.append(new_player)  # change to database
            new_player.socket_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            new_player.socket_server.bind(('0.0.0.0', 0))
            threading.Thread(target=receive, daemon=True, args=(new_player.socket_server,)).start()
        else:
            current_player = player.Player(nickname='Glidaria', ip=0, key=0, Class='tmp')
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
                    if nickname.index('!') == -1:
                        file = open(f"../Database/{username_hash}.txt", 'rb')
                        file.close()
                        udp_server_socket.sendto('sdenyaccess'.encode(), current_player.socket_send)
                    else:
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
                    for Mo in mobs:
                        packet = f'm{int(Mo.lvl)}|{int(Mo.x)}|{int(Mo.y)}|{int(Mo.health)}|{Mo.is_melee}'
                        udp_server_socket.sendto(packet.encode(), current_player.socket_send)
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
                        for Mo in mobs:
                            packet = f'm{int(Mo.lvl)}|{int(Mo.x)}|{int(Mo.y)}|{int(Mo.health)}|{Mo.is_melee}'
                            udp_server_socket.sendto(packet.encode(), current_player.socket_send)
                    else:
                        raise Exception
                except:
                    udp_server_socket.sendto('ldenyaccess'.encode(), current_player.socket_send)
            elif data.startswith('U'):
                print("Received heal packet")
                if current_player.use_potion():
                    packet = f'L{current_player.x}.{current_player.y}.{current_player.Class}.{current_player.nickname}.{current_player.health}'
                    udp_server_socket.sendto(packet.encode(), current_player.socket_send)
                    packet = f'G{current_player.gold}'
                    udp_server_socket.sendto(packet.encode(), current_player.socket_send)
            elif data.startswith('R'):
                if not current_player.inventory[current_player.picked]:
                    for itemC in items_on_surface:
                        if itemC.check_pick_up(p=current_player):
                            items_on_surface.remove(itemC)
                            current_player.inventory[current_player.picked] = item.Item(name=itemC.name, lvl=itemC.lvl)
                            inventory = ''
                            for itemB in current_player.inventory:
                                if itemB:
                                    inventory += f'{itemB.name},{itemB.lvl}'
                                else:
                                    inventory += "False"
                                inventory += '@'
                            inventory = inventory[:-1]
                            packet = f'I{inventory}'
                            udp_server_socket.sendto(packet.encode(), current_player.socket_particles)
                            packet = f'W{itemC.id}'
                            for player1 in players:
                                if player1.Class != 'tmp':
                                    player1.socket_server.sendto(packet.encode(), player1.socket_mobs)
            elif data == "L":
                print("leaving")
                print(current_player.x, current_player.y)
                if current_player in players:
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
                current_player.attack(mouseX=int(target_x), mouseY=int(target_y))
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
                print("Received item removal request")
                itemE = current_player.inventory[current_player.picked]
                if itemE:
                    items_on_surface.append(
                        dropped_item.Dropped_item(x=current_player.x, y=current_player.y, lvl=itemE.lvl,
                                                  name=itemE.name, time_dropped=time.time()))
                    current_player.inventory[current_player.picked] = False
                    packet = f'${-1}|{int(current_player.x)}|{int(current_player.y)}|{itemE.name}'
                    for player1 in players:
                        if player1 != 'tmp':
                            udp_server_socket.sendto(packet.encode(), current_player.socket_particles)
                    inventory = ''
                    for itemB in current_player.inventory:
                        if itemB:
                            inventory += f'{itemB.name},{itemB.lvl}'
                        else:
                            inventory += "False"
                        inventory += '@'
                    inventory = inventory[:-1]
                    packet = f'I{inventory}'
                    udp_server_socket.sendto(packet.encode(), current_player.socket_particles)
        clock.tick(30)


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
                                player2.socket_server.sendto(packet.encode(), player2.socket_location)
                move_particles_for_entity(entity=player1)
        clock.tick(30)


def move_particles_for_entity(entity):
    for particle in entity.projectiles:
        packet = ''
        if particle.first_move:
            packet = f'2{particle.x}|{particle.y}|{particle.angle}|{particle.name}|{particle.id_of_particle}|{particle.dmg}|{particle.range}|{particle.speed}'
            try:
                packet = packet + f'|{entity.nickname}'
            except:
                packet = packet + '|!'
            print(packet)
        elif particle.range <= 0 or (particle.hit and particle.speed != 1):
            packet = f'7{particle.id_of_particle}'
            entity.projectiles.remove(particle)
        if packet != '':
            print("Sending particle packet..")
            for player1 in players:
                if player1.Class != 'tmp':
                    player1.socket_server.sendto(packet.encode(), player1.socket_particles)
        particle.move(entity=entity)


def identify_par_dmg(Ps: list, Ms: list):
    while True:
        """
        gotta have a thread for itself and the list should be globals
        :param Ps: A list of all the players that exist in the game
        :param Ms: A list of the mobs
        :return: new health for each entity
        """
        for M in Ms:
            for S in M.projectiles:
                for P in Ps:
                    P_rect.center = P.x, P.y
                    if P_rect.colliderect(S.hit_box) and not S.hit:
                        S.hit = True
                        P.health -= int(10 * P.income_dmg_multiplier)
                        if P.health <= 0:
                            P.health = 0
                        packet = f"L{P.x}.{P.y}.{P.Class}.{P.nickname}.{P.health}"
                        for player1 in players:
                            player1.socket_server.sendto(packet.encode(), player1.socket_location)
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
                                packet = f'G{P1.gold}'
                                P1.socket_server.sendto(packet.encode(), P1.socket_send)
                                M.death_time = time.time()
                                M.is_alive = False
                                D_item = generate_drop(M.x, M.y, M.lvl)
                                items_on_surface.append(D_item)
                                packet = f'${int(M.lvl)}|{int(M.x)}|{int(M.y)}|{D_item.name}'
                                for player1 in players:
                                    if player1.Class != 'tmp':
                                        player1.socket_server.sendto(packet.encode(), player1.socket_mobs)

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
                                player1.socket_server.sendto(packet.encode(), player1.socket_location)
        clock.tick(30)


def generate_drop(x, y, average):
    lvl = abs(random.randint(average - 11, average + 9)) + 1
    name = random.randint(0, 2)
    if name == 0:
        return dropped_item.Dropped_item(x, y, lvl, 'bow', time.time())
    elif name == 1:
        return dropped_item.Dropped_item(x, y, lvl, 'dagger', time.time())
    return dropped_item.Dropped_item(x, y, lvl, "cumball", time.time())


def move_none_players(mobs: list, items_on_surface: list):
    while 1:
        for Mo in mobs:
            packet = ''
            if Mo.is_alive:
                if Mo.move(players=players):
                    packet = f'm{int(Mo.lvl)}|{int(Mo.x)}|{int(Mo.y)}|{int(Mo.health)}|{Mo.is_melee}'
                    print('Mob moved')
            elif time.time() - Mo.death_time >= 7:
                Mo.is_alive = True
                Mo.x, Mo.y = Mo.home_x, Mo.home_y
                Mo.health = 100 * Mo.lvl
                Mo.death_time = 0
                packet = f'm{int(Mo.lvl)}|{int(Mo.x)}|{int(Mo.y)}|{int(Mo.health)}|{Mo.is_melee}'
            if packet != '':
                for player1 in players:
                    if player1.Class != 'tmp':
                        player1.socket_server.sendto(packet.encode(), player1.socket_mobs)
            move_particles_for_entity(entity=Mo)
        for D_item in items_on_surface:
            if time.time() - D_item.time_dropped > 7:
                items_on_surface.remove(D_item)
                packet = f'W{D_item.id}'
                for player1 in players:
                    if player1.Class != 'tmp':
                        player1.socket_server.sendto(packet.encode(), player1.socket_mobs)
        clock.tick(30)


def main():
    threading.Thread(target=receive, daemon=True, args=(login_server_socket,)).start()
    threading.Thread(target=move_players, daemon=True).start()
    threading.Thread(target=identify_par_dmg, daemon=True, args=(players, mobs,)).start()
    threading.Thread(target=move_none_players, daemon=True, args=(mobs, items_on_surface,)).start()
    while True:
        clock.tick(30)


if __name__ == '__main__':
    main()
