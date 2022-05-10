import threading
import pygame
import socket
from Classes import dropped_item, player, mob, encryption, item

udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_server_socket.bind(('0.0.0.0', 42069))
players = []


def receive():
    while True:
        data, ip = udp_server_socket.recvfrom(1024)
        data = data.decode()
        if data.startswith('hi'):
            print("new player connected")
            players.append(player.Player(nickname='yamete~kudenasai', ip=ip, key=0, Class='tmp'))  # change to database
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
                    print(password_hash_in_db)
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
                        x = 5 / 0
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
                    f'{current_player.nickname}\n{password}\n{current_player.Class}\n{current_player.x}\n{current_player.y}\n{current_player.gold}\n{current_player.health}\n{inventory}')
                file.close()
                print(
                    f'{current_player.nickname}\n{password}\n{current_player.Class}\n{current_player.x}\n{current_player.y}\n{current_player.gold}\n{current_player.health}\n{inventory}')


def send():
    screen_rect = pygame.Rect((0,0), (1920, 1080))
    player_rect = pygame.Rect((0, 0), (66, 92))
    while True:
        for player in players:
            other_packets = 'o'
            screen_rect.center = player.x, player.y
            for player2 in players:
                player_rect.center = player2.x, player2.y
                if player2.nickname != player.nickname and screen_rect.colliderect(player_rect):
                    other_packets += f'{player2.nickname}.{player2.x}.{player2.y}.{player2.Class}.{player2.health}@'
            other_packets = other_packets[:-1]
            if other_packets:
                udp_server_socket.sendto(other_packets.encode(), player.ip)


def move_players():
    while 1:
        for player in players:
            if player.Class != 'tmp':
                if player.move():
                    packet = f"L{player.x}.{player.y}"
                    udp_server_socket.sendto(packet.encode(), player.ip)


def main():
    threading.Thread(target=receive, daemon=True).start()
    threading.Thread(target=move_players, daemon=True).start()
    threading.Thread(target=send, daemon=True).start()
    while 1:
        pass


if __name__ == '__main__':
    main()
