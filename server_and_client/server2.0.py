import threading
import pygame
import socket
from Classes import player, item

udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_server_socket.bind(('0.0.0.0', 42069))
players = []


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
                if check_player.ip == ip:
                    current_player = check_player
                    break
            if data.startswith('M'):
                print("player changed direction")
                x_dir, y_dir = data[1:].split('.')
                current_player.dir_x = int(x_dir)
                current_player.dir_y = int(y_dir)
            elif data.startswith('s'):
                print('sign up received')
                nickname, username_hash, password_hash, Class = data[1:].split('.')
                try:
                    file = open(f"../Database/{username_hash}.txt", 'rb')
                    file.close()
                    udp_server_socket.sendto('sdenyaccess'.encode(), current_player.ip)
                except:
                    file = open(f"../Database/{username_hash}.txt", 'a+')
                    x, y, gold, health = 1000, 1000, 0, 100
                    inventory = "bow,1@False@False@False@False@False"
                    file.write(f'{nickname}\n{password_hash}\n{Class}\n{x}\n{y}\n{gold}\n{health}\n{inventory}')
                    file.close()
                    current_player.Class = Class
                    current_player.nickname = nickname
                    udp_server_socket.sendto('sallow'.encode(), current_player.ip)
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
                        udp_server_socket.sendto(
                            f"lallow{nickname}.{Class}.{x}.{y}.{gold}.{health}.{inventory}".encode(), current_player.ip)
                        current_player.Class = Class
                        current_player.nickname = nickname
                        current_player.x = int(x)
                        current_player.y = int(y)
                        current_player.username = username_hash
                        for i, itema in enumerate(inventory.split('@')):
                            if itema == "False":
                                current_player.inventory[i] = False
                            else:
                                current_player.inventory[i] = item.Item(itema.split(",")[0], int(itema.split(",")[1]))
                    else:
                        raise Exception
                except:
                    udp_server_socket.sendto('ldenyaccess'.encode(), current_player.ip)
            elif data == "L":
                print("leaving")
                players.remove(current_player)
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
                    if current_player.is_ability_active:
                        packet = 'a'
                        udp_server_socket.sendto(packet.encode(), current_player.ip)


def send():
    screen_rect = pygame.Rect((0, 0), (1920, 1080))
    player_rect = pygame.Rect((0, 0), (66, 92))
    while True:
        for player1 in players:
            other_packets = 'o'
            particles_packet = '2'
            screen_rect.center = player1.x, player1.y
            for player2 in players:
                player_rect.center = player2.x, player2.y
                if player2.nickname != player1.nickname and screen_rect.colliderect(player_rect):
                    other_packets += f'{player2.nickname}.{player2.x}.{player2.y}.{player2.Class}.{player2.health}@'
                for particle in player2.projectiles:
                    if screen_rect.colliderect(particle.hit_box):
                        particles_packet += f'{particle.x}|{particle.y}|{particle.angle}|{particle.name}@'
            particles_packet = particles_packet[:-1]
            other_packets = other_packets[:-1]
            if other_packets:
                udp_server_socket.sendto(other_packets.encode(), player1.ip)
            if particles_packet:
                print(particles_packet)
                udp_server_socket.sendto(particles_packet.encode(), player1.ip)


def move_players():
    while 1:
        for player1 in players:
            player_screen = pygame.Rect((0, 0), (1920, 1080))
            player_rect = pygame.Rect((0, 0), (66, 92))
            player_rect.center = player1.x, player1.y
            if player1.Class != 'tmp':
                for player2 in players:
                    if player2.Class != 'tmp':
                        player_screen.center = player2.x, player2.y
                        if player_screen.colliderect(player_rect):
                            packet = f'o{player1.x}.{player1.y}.{player1.Class}.{player1.nickname}.{player1.health}'
                            udp_server_socket.sendto(packet.encode(), player2.ip)
                player1.ability()
                if player1.move():
                    packet = f"L{player1.x}.{player1.y}"
                    udp_server_socket.sendto(packet.encode(), player1.ip)
            move_particles_for_entity(entity=player1)

#
def move_particles_for_entity(entity):
    for particle in entity.projectiles:
        screen_rect = pygame.Rect((0, 0), (1920, 1080))
        particle.move(entity.x, entity.y)
        packet = f'2{particle.x}|{particle.y}|{particle.angle}|{particle.name}'
        for player1 in players:
            screen_rect.center = player1.x, player1.y
            if screen_rect.colliderect(particle.hit_box):
                udp_server_socket.sendto(packet.encode(), player1.ip)
        if particle.range <= 0:
            packet = f'7{particle.x}|{particle.y}|{particle.angle}|{particle.name}'
            entity.projectiles.remove(particle)
            for player1 in players:
                screen_rect.center = player1.x, player1.y
                if screen_rect.colliderect(particle.hit_box):
                    udp_server_socket.sendto(packet.encode(), player1.ip)


def main():
    threading.Thread(target=receive, daemon=True).start()
    threading.Thread(target=move_players, daemon=True).start()
    # threading.Thread(target=send, daemon=True).start()
    while 1:
        pass


if __name__ == '__main__':
    main()
