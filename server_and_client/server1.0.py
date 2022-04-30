import pygame
import socket
import time
import threading
import random
from Classes import dropped_item, player, mob, encryption, item, packet_builder

pygame.init()
P_rect = pygame.Rect((0, 0), (66, 92))
M_rect = pygame.Rect((0, 0), (88, 120))
items_on_surface = []  #
mobs = []
players = []
chat_list = []

udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_server_socket.bind(('0.0.0.0', 42069))


def time_to_string(t):
    return f'{int(t // 3600)}:{int(t // 60)}:{int(t // 1)}'


def identify_par_dmg():
    """
    got to have a thread for itself and the list should be globals
    :return: new health for each entity
    """
    while True:
        for M in mobs:
            for S in M.projectiles:
                for P in players:
                    if P.Class != 'tmp':
                        P_rect.center = P.x, P.y
                        if P_rect.colliderect(S.hit_box) and not S.hit:
                            M.projectiles.remove(S)
                            S.hit = True
                            P.health -= int(10 * P.income_dmg_multiplier)
                            if P.health <= 0:
                                players.remove(P)
        for P1 in players:
            if P1.Class != 'tmp':
                for par in P1.projectiles:
                    for M in mobs:
                        if M.is_alive:
                            M_rect.center = M.x, M.y
                            if M_rect.colliderect(par.hit_box) and not par.hit:
                                par.hit = True
                                if par.speed != 1:
                                    P1.projectiles.remove(par)
                                M.health -= par.dmg
                                if M.health <= 0:
                                    P1.gold += M.worth
                                    M.death_time = time.time()
                                    M.is_alive = False
                                    items_on_surface.append(generate_drop(M.x, M.y, M.lvl))
                    for P2 in players:
                        if P2.Class != 'tmp':
                            if P2.nickname != P1.nickname:
                                P2_rect = pygame.Rect((0, 0), (66, 92))
                                P2_rect.center = P2.x, P2.y
                                if P2_rect.colliderect(par.hit_box) and not par.hit:
                                    par.hit = True
                                    if par.speed != 1:
                                        P1.projectiles.remove(par)
                                    P2.health -= int(par.dmg * P2.income_dmg_multiplier)
                                    if P2.health <= 0:
                                        players.remove(P2)


def generate_drop(x, y, average):
    lvl = abs(random.randint(average - 11, average + 9)) + 1
    name = random.randint(0, 2)
    if name == 0:
        return dropped_item.Dropped_item(x, y, lvl, 'bow', time.time())
    elif name == 1:
        return dropped_item.Dropped_item(x, y, lvl, 'dagger', time.time())
    return dropped_item.Dropped_item(x, y, lvl, "cumball", time.time())


def move_all_players_and_their_particles():  # this function gotta have a thread
    while True:
        for Pl in players:
            if Pl.Class != 'tmp':
                Pl.move()
                Pl.ability()
                move_particles_for_entity(entity=Pl)


def move_all_mobs_and_their_spear():  # this function gotta have a thread
    while True:
        for Mo in mobs:
            if Mo.is_alive:
                Mo.move(players=players)
            elif time.time() - Mo.death_time >= 7:
                Mo.is_alive = True
                Mo.x, Mo.y = Mo.home_x, Mo.home_y
                Mo.health = 100 * Mo.lvl
            move_particles_for_entity(entity=Mo)


def move_particles_for_entity(entity):
    for particle in entity.projectiles:
        if particle.range <= 0:
            entity.projectiles.remove(particle)
        particle.move(entity.x, entity.y)


def receive_packet_and_handle_it(start_time):
    while True:
        message, ip = udp_server_socket.recvfrom(1024)
        message = message.decode()
        if message.startswith('hi'):
            threading.Thread(target=receive_packet_and_handle_it, args=(start_time,), daemon=True).start()
            # the packet look like - hiN.E
            message = message[2:]
            n, e = message.split('.')
            n = int(n)
            e = int(e)
            key_rsa = encryption.rsa.key.PublicKey(e=e, n=n)
            custom_key = encryption.genKey(5)
            new_player = player.Player(nickname='tmp', ip=ip, key=custom_key, Class='tmp')
            players.append(new_player)
            message_for_new_client = encryption.encrypt_rsa(msg=custom_key, key=key_rsa)
            udp_server_socket.sendto(message_for_new_client, ip)
        else:
            # here it is a client that was connected before so all the packets are encrypted
            key = ''
            P_for_changes = player.Player(0, 0, 0, 0)
            for P in players:
                if P.ip == ip:  #
                    key = P.key
                    P_for_changes = P
                    break
            message = encryption.decrypt(msg=message, key=key)
            syn = message[:3]
            message = message[3:]
            if syn == P_for_changes.expected_syn:
                P_for_changes.expected_syn += 1
                # here should be Guy's loop like while message:
                if message.startswith('sign_up'):
                    # packet format is sign_upNickName,UserNameHash,PasswordHash,Class
                    sign_up_data = message[:7]
                    nick_name, user_name_hash, password_hash, chosen_class = sign_up_data.split(',')
                    P_for_changes.nickname = nick_name
                    P_for_changes.Class = chosen_class
                    # database.write info if username and nickname aren't taken
                elif message.startswith('log_in'):
                    # packet format is log_inUserNameHash,PasswordHash
                    log_in_data = message[:6]
                    user_name_hash, password_hash = log_in_data.split(',')
                    # if the data is valid
                    if data_is_valid(user_name_hash,
                                     data_is_valid(username=user_name_hash, password=password_hash)):
                        nick_name = 'lidor'
                        chosen_class = 'Tank'  # should be loaded from database
                        x = 0  # should be loaded from database
                        y = 0  # should be loaded from database
                        inventory = [False, False, False, False, False, False]  # should be loaded from data bse
                        P_for_changes.Class = chosen_class
                        P_for_changes.nickname = nick_name
                        P_for_changes.x = x
                        P_for_changes.y = y
                        # send log in accept
                        # P_for_changes.inventory = inventory
                    else:
                        # send log in deny
                        print('deny access')
                    # send log in accept
                elif message.startswith('move'):
                    # packet format is move-1.-1
                    move_data = message[4:]
                    x_dir, y_dir = move_data.split('.')
                    P_for_changes.dir_x = int(x_dir)
                    P_for_changes.dir_y = int(y_dir)
                elif message.startswith('attack'):
                    # packet format is attackX.Y
                    attack_data = message[6:]
                    x_target, y_target = attack_data.split('.')
                    P_for_changes.attack(mouseX=int(x_target),
                                         mouseY=int(y_target))  # can add argument of picked here
                elif message.startswith('pick'):
                    # packet format is pick5
                    pick_data = message[4:]
                    P_for_changes.picked = int(pick_data)
                elif message.startswith('sell') and P_for_changes.inventory[P_for_changes.picked]:
                    # packet = sell
                    P_for_changes.gold += P_for_changes.inventory[P_for_changes.picked].upgrade_cost * 0.75
                    P_for_changes.inventory[P_for_changes.picked] = False
                elif message.startswith('chat'):
                    # packet = chat"message"
                    chat_data = message[4:]
                    chat_list.append(
                        f'({P_for_changes.nickname}): {chat_data} [{time_to_string(time.time() - start_time)}]')
                elif message.startswith('pick-up'):
                    # packet format is "pickup"
                    for item_on_surface in items_on_surface:
                        if item_on_surface.check_pick_up(P_for_changes):
                            if P_for_changes.inventory[P_for_changes.picked]:
                                P_for_changes.gold += P_for_changes.inventory[
                                                          P_for_changes.picked].upgrade_cost * 0.6
                            P_for_changes.inventory[P_for_changes.picked] = item.Item(item_on_surface.name,
                                                                                      item_on_surface.lvl)
                            items_on_surface.remove(item_on_surface)
                            break
                elif message.startswith('upgrade') and P_for_changes.inventory[P_for_changes.picked].lvl < 999 and \
                        P_for_changes.inventory[P_for_changes.picked].upgrade_cost <= P_for_changes.gold:
                    # packet format is "upgrade"
                    P_for_changes.gold -= P_for_changes.inventory[P_for_changes.picked].upgrade_cost
                    P_for_changes.inventory[P_for_changes.picked].upgrade()
                elif message.startswith('leave'):
                    # packet format is "leave"
                    players.remove(P_for_changes)
                    return
                elif message.startswith('potion'):
                    # packet format is "potion"
                    P_for_changes.use_potion()
                elif message.startswith('ability'):
                    # packet format is "ability"
                    P_for_changes.use_ability()
                elif message.startswith('still-alive'):
                    P_for_changes.last_time_send_connection_alive_packet = time.time()
                elif message.startswith('swap'):
                    # packet format is "swap0
                    P_for_changes.inventory[P_for_changes.picked], P_for_changes.inventory[int(message[4])] = \
                        P_for_changes.inventory[int(message[4])], P_for_changes.inventory[P_for_changes.picked]
                elif message.startswith('scroll'):
                    scroll_data = int(message[6:])
                    P_for_changes.picked += scroll_data
                    P_for_changes.picked %= 6


def check_players_that_lost_connection():
    disconnect_time = 20
    while 1:
        for P in players:
            if time.time() - P.last_time_send_connection_alive_packet > disconnect_time:
                players.remove(P)


def create_mobs():
    for i in range(10):
        for k in range(10):
            mobs.append(mob.Mob(x=7680 * i + 960, y=4320 * k + 540, lvl=10 * i + k + 1))


def read_from_data_base():
    # database should look like player: nickname,username,password,x,y,inventory,Class,gold,health
    # return all of this as a list
    return ['a', 'b']


def write_to_data_base():
    pass


def send_data():
    while 1:
        for P in players:
            packet = packet_builder.buildAllServer(player=P, chatMsg='')
            encrypted_packet = encryption.encrypt(msg=packet, key=P.key)
            udp_server_socket.sendto(encrypted_packet.encode(), P.ip)
            # Lidor gotta do it
            # build packet for player
            # send the packet


def data_is_valid(username, password):
    data = read_from_data_base()
    if username in data and password in data:
        return data[data.index(username) + 1] == password
    return False


def main():
    start_time = time.time()
    create_mobs()
    threading.Thread(target=receive_packet_and_handle_it, args=(start_time,), daemon=True).start()
    threading.Thread(target=move_all_mobs_and_their_spear, daemon=True).start()
    threading.Thread(target=move_all_players_and_their_particles, daemon=True).start()
    threading.Thread(target=identify_par_dmg, daemon=True).start()
    threading.Thread(target=check_players_that_lost_connection, daemon=True).start()
    while 1:
        pass
    # todo:
    #   data base
    #   feel in the blank functions
    #   exception hooking


if __name__ == '__main__':
    main()
