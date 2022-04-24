import pygame
import socket
import time
import threading
import random
from Classes import dropped_item, player, mob, encryption

pygame.init()
P_rect = pygame.Rect((0, 0), (66, 92))
M_rect = pygame.Rect((0, 0), (88, 120))
items_on_surface = []
mobs = []
players = []
chat_list = []

udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_server_socket.bind(('0.0.0.0', 69420))


def identify_par_dmg():
    """
    gotaa have a thread for itself and the list should be globals
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


def recv(start_time):
    while True:
        message, ip = udp_server_socket.recvfrom(1024)
        message = message.decode()
        if message.startswith('hi'):
            threading.Thread(target=recv, args=(start_time,), daemon=True).start()
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
            # here it is a client that was conecnted before so all the packets are encrypted
            key = ''
            P_for_changes = player.Player(0, 0, 0, 0)
            for P in players:
                if P.ip == ip:
                    key = P.key
                    P_for_changes = P
                    break
            message = encryption.decrypt(msg=message, key=key)

            # here should be Guy's loop like while message: and shit

            if message.startswith('sign_up'):
                # packet format is sign_upNickName,UserNameHash,PasswordHash,Class
                message = message[:7]
                nick_name, user_name_hash, password_hash, chosen_class = message.split(',')
                P_for_changes.nickname = nick_name
                P_for_changes.Class = chosen_class
                # database.write info if username and nickname aren't taken
            elif message.startswith('log_in'):
                # packet format is log_inUserNameHash,PasswordHash
                message = message[:6]
                user_name_hash, password_hash = message.split(',')
                # if the data is valid
                if True:
                    nick_name = 'should be loaded from data base'
                    chosen_class = 'Tank'  # should be loaded from data base
                    P_for_changes.Class = chosen_class
                    P_for_changes.nickname = nick_name
                else:
                    # send log in deny
                    print('deny acsses')
                # send log in accept
            elif message.startswith('move'):
                # packet format is move-1.-1
                message = message[4:]
                x_dir, y_dir = message.split('.')
                P_for_changes.dir_x = int(x_dir)
                P_for_changes.dir_y = int(y_dir)
            elif message.startswith('attack'):
                # packet format is attackX.Y
                message = message[6:]
                x_target, y_target = message.split('.')
                P_for_changes.attack(mouseX=int(x_target), mouseY=int(y_target))  # can add argument of picked here
            elif message.startswith('pick'):
                # packet format is pickSlot
                message = message[4:]
                P_for_changes.picked = int(message)
            elif message.startswith('sell') and P_for_changes.inventory[P_for_changes.picked]:
                # packet = sell
                P_for_changes.gold += P_for_changes.inventory[P_for_changes.picked].upgrade_cost * 0.75
                P_for_changes.inventory[P_for_changes.picked] = False
            elif message.startswith('chat'):
                # packet = chat"message"
                message = message[4:]
                chat_list.append(f'({P_for_changes.nickname}): {message} [{time_to_string(time.time() - start_time)}]')
            elif message.startswith('pickup'):
                # packet format is "pickup"
                for item_on_surface in items_on_surface:
                    if item_on_surface.check_pick_up(P_for_changes):
                        if P_for_changes.inventory[P_for_changes.picked]:
                            P_for_changes.gold += P_for_changes.inventory[P_for_changes.picked].upgrade_cost * 0.6
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


def create_mobs():
    for i in range(10):
        for k in range(10):
            mobs.append(mob.Mob(x=7680 * i + 960, y=4320 * k + 540, lvl=10 * i + k + 1))


def read_from_data_base():
    pass


def write_to_data_base():
    pass


def send_data():
    pass


def main():
    start_time = time.time()
    create_mobs()
    threading.Thread(target=recv, args=(start_time,), daemon=True).start()
    threading.Thread(target=move_all_mobs_and_their_spear(), daemon=True).start()
    threading.Thread(target=move_all_players_and_their_particles(), daemon=True).start()
    threading.Thread(target=identify_par_dmg(), daemon=True)
    # todo:
    #   data base
    #   feel in the blank functions
    #   exception hooking


if __name__ == '__main__':
    main()