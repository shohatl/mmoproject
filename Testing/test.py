import random
import sys
import time

import pygame

from Classes import player, mob, item, dropped_item, config

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
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


def time_to_string(t):
    return f'{int(t // 3600)}:{int(t // 60)}:{int(t // 1)}'


def identify_par_dmg(Ps: list, Ms: list):
    """
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
                        Ps.remove(P)
    for P1 in Ps:
        for par in P1.projectiles:
            for M in Ms:
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
            for P2 in Ps:
                if P2.nickname != P1.nickname:
                    P2_rect = pygame.Rect((0, 0), (66, 92))
                    P2_rect.center = P2.x, P2.y
                    if P2_rect.colliderect(par.hit_box) and not par.hit:
                        par.hit = True
                        if par.speed != 1:
                            P1.projectiles.remove(par)
                        P2.health -= int(par.dmg * P2.income_dmg_multiplier)
                        if P2.health <= 0:
                            Ps.remove(P2)


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


def show_inventory(P: player.Player):
    slot_rect = pygame.Rect((screen.get_size()[0] - 490, screen.get_size()[1] - 90), (90, 90))
    in_hand_x, in_hand_y = 0, 0
    for i, I in enumerate(P.inventory):
        pygame.draw.rect(screen, (100, 100, 100), slot_rect, 10)
        if i == P.picked:
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


def show_time(start_time):
    text_rect = font.render(time_to_string(time.time() - start_time), True, (255, 255, 255)).get_rect()
    text_rect.topright = screen.get_size()[0], 0
    screen.blit(font.render(time_to_string(time.time() - start_time), True, (255, 255, 255)), text_rect)


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


def generate_drop(x, y, average):
    lvl = abs(random.randint(average - 11, average + 9)) + 1
    name = random.randint(0, 2)
    if name == 0:
        return dropped_item.Dropped_item(x, y, lvl, 'bow', time.time())
    elif name == 1:
        return dropped_item.Dropped_item(x, y, lvl, 'dagger', time.time())
    return dropped_item.Dropped_item(x, y, lvl, "cumball", time.time())


def update_player_direction_based_on_input(P2: player.Player, P: player.Player):
    keys = pygame.key.get_pressed()
    P.dir_x = keys[pygame.K_d] - keys[pygame.K_a]
    P.dir_y = keys[pygame.K_s] - keys[pygame.K_w]
    P2.dir_x = keys[pygame.K_l] - keys[pygame.K_j]
    P2.dir_y = keys[pygame.K_k] - keys[pygame.K_i]


def move_all_players_and_their_particles(players: list):
    for Pl in players:
        Pl.move()
        Pl.ability()
        move_particles_for_entity(entity=Pl)


def move_all_mobs_and_their_spear(mobs: list, players: list):
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


def show_background(x, y, img):
    screen.blit(img, (0, 0), ((x % img.get_width(), y % img.get_height()), screen.get_size()))
    screen.blit(img, (img.get_width() - x % img.get_width(), img.get_height() - y % img.get_height()))
    screen.blit(img, (0 - x % img.get_width(), img.get_height() - y % img.get_height()))
    screen.blit(img, (img.get_width() - x % img.get_width(), 0 - y % img.get_height()))


def handle_input(P: player.Player, settings: config.Config, start_time: float, camera_x: int, camera_y: int):
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and settings.chat_enabled:
                settings.in_chat = not settings.in_chat
                if not settings.in_chat:
                    if settings.chat_message:
                        while len(settings.chat_log) >= 5:
                            settings.chat_log = settings.chat_log[1:]
                        settings.chat_log.append(
                            f'({P.nickname}): {settings.chat_message} [{time_to_string(time.time() - start_time)}]')
                        settings.chat_message = ''
                else:
                    P.dir_x = 0
                    P.dir_y = 0
            elif settings.in_chat:
                if len(settings.chat_message) < 45 and '~' >= event.unicode >= ' ':
                    settings.chat_message += event.unicode
            elif event.key == pygame.K_TAB:
                settings.chat_enabled = not settings.chat_enabled
            elif event.key == pygame.K_e:
                P.use_ability()
            elif event.key == pygame.K_x and P.inventory[P.picked]:
                P.gold += P.inventory[P.picked].upgrade_cost * 0.75
                P.inventory[P.picked] = False
            elif event.key == pygame.K_q:
                for item_on_surface in items_on_surface:
                    if item_on_surface.check_pick_up(P):
                        if P.inventory[P.picked]:
                            P.gold += P.inventory[P.picked].upgrade_cost * 0.6
                        P.inventory[P.picked] = item.Item(item_on_surface.name, item_on_surface.lvl)
                        items_on_surface.remove(item_on_surface)
                        break
            elif event.key == pygame.K_u and P.inventory[P.picked].lvl < 999\
                    and P.inventory[P.picked].upgrade_cost <= P.gold:
                P.gold -= P.inventory[P.picked].upgrade_cost
                P.inventory[P.picked].upgrade()
            elif event.key == pygame.K_p:
                P.use_potion()
            elif pygame.K_1 <= event.key <= pygame.K_6:
                P.picked = int(event.unicode) - 1
            elif event.key == pygame.K_y:
                settings.camera_locked = not settings.camera_locked
        elif event.type == pygame.MOUSEBUTTONDOWN and not settings.in_chat:
            if event.button == 1 and P.inventory[P.picked]:
                m_x, m_y = pygame.mouse.get_pos()
                P.attack(mouseX=m_x + camera_x, mouseY=m_y + camera_y)
            elif event.button == 4:
                P.picked += 1
                P.picked %= 6
            elif event.button == 5:
                P.picked -= 1
                P.picked %= 6


def main():
    ar = [1,2,3,4,5,6,7,8,9]
    print(ar)
    ar = ar[3:]
    print(ar)


    settings = config.Config()
    P = player.Player(nickname="Hunnydrips", key=0, ip=0, Class='Scout')
    camera_x = 0
    camera_y = 0
    map_img = pygame.image.load('../Assets/basics/ground2.jpg')
    start_time = time.time()
    frame_counter = 0
    CL = pygame.time.Clock()
    P2 = player.Player(nickname="Glidaria", key=0, ip=0, Class='Mage')
    M = mob.Mob(x=50, y=50, lvl=5)
    M2 = mob.Mob(x=500, y=50, lvl=3)
    players = [P, P2]
    mobs = [M, M2]
    running = True

    while running:
        screen.fill((0, 0, 255))
        frame_counter += 1
        frame_counter %= 60
        keys = pygame.key.get_pressed()
        handle_input(P=P, settings=settings, start_time=start_time, camera_x=camera_x, camera_y=camera_y)
        if not settings.in_chat:
            update_player_direction_based_on_input(P2=P2, P=P)  # client

        # ------------------ update all locations data
        move_all_players_and_their_particles(players=players)  # server
        move_all_mobs_and_their_spear(mobs=mobs, players=players)  # server
        identify_par_dmg(Ps=players, Ms=mobs)  # server
        # --------------------------------
        if settings.camera_locked:
            camera_x = P.x - screen.get_width() // 2
            camera_y = P.y - screen.get_height() // 2
        else:
            camera_x -= 20 * (keys[pygame.K_LEFT] - keys[pygame.K_RIGHT])
            camera_y += 20 * (keys[pygame.K_DOWN] - keys[pygame.K_UP])
        show_background(x=camera_x, y=camera_y, img=map_img)

        # show all the entities
        for M in mobs:
            show_entities_and_their_particles(entity=M, cx=camera_x, ch=camera_y)
        for Pl in players:
            show_entities_and_their_particles(entity=Pl, cx=camera_x, ch=camera_y)
        # -----------------

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
            if keys[pygame.K_BACKSPACE] and settings.chat_message and not frame_counter % 4:
                settings.chat_message = settings.chat_message[:-1]
            screen.blit(chat_box, (10, 200))
            blinking_shit = ''
            if frame_counter < 30:
                blinking_shit = '|'
            screen.blit(font.render(settings.chat_message + blinking_shit, True, (255, 255, 255)), (13, 205))
        # ------------------------------------

        # --------------- remove on floor items
        for item_on_surface in items_on_surface:
            if time.time() - item_on_surface.time_dropped > 7:
                items_on_surface.remove(item_on_surface)
            item_on_surface.x -= camera_x
            item_on_surface.y -= camera_y
            item_on_surface.show_item_on_surface(screen=screen)
            item_on_surface.x += camera_x
            item_on_surface.y += camera_y
        # -------------------------------------
        show_inventory(P=P)  # client
        show_time(start_time=start_time)  # client
        show_gold(gold=P.gold)  # client
        show_ability_cool_down(P=P, camera_x=camera_x, camera_y=camera_y)  # client
        CL.tick(60)
        pygame.display.update()


if __name__ == '__main__':
    main()
