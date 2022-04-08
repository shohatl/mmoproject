import sys
import time
import pygame
from Classes import player, mob

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
font = pygame.font.Font("freesansbold.ttf", 20)
font_gold = pygame.font.Font("freesansbold.ttf", 100)

gold_coin = pygame.image.load('../Assets/coins/gold.png')
silver_coin = pygame.image.load('../Assets/coins/silver.png')
bronze_coin = pygame.image.load('../Assets/coins/bronze.png')

gold_coin = pygame.transform.scale(gold_coin, (70, 70))
silver_coin = pygame.transform.scale(silver_coin, (70, 70))
bronze_coin = pygame.transform.scale(bronze_coin, (70, 70))


def draw_gold(gold: int):
    screen.blit(gold_coin, (35, 950))
    screen.blit(silver_coin, (0, 1010))
    screen.blit(bronze_coin, (70, 1010))
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
    screen.blit(toShow, (150, 970))



def identify_par_dmg(Ps: list, Ms: list):
    """
    :param Ps: A list of all the players that exist in the game
    :param Ms: A list of the mobs
    :return: new health for each entity
    """
    for M in Ms:
        for S in M.spears:
            for P in Ps:
                P_rect = pygame.Rect((0, 0), (100, 100))
                P_rect.center = P.x, P.y
                if P_rect.colliderect(S.hit_box) and not S.hit:
                    M.spears.remove(S)
                    S.hit = True
                    P.health -= int(10 * P.income_dmg_multiplier)
                    if P.health <= 0:
                        Ps.remove(P)
    for P1 in Ps:
        for par in P1.projectiles:
            for M in Ms:
                if M.is_alive:
                    M_rect = pygame.Rect((0, 0), (100, 100))
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
            for P2 in Ps:
                if P2.nickname != P1.nickname:
                    P2_rect = pygame.Rect((0, 0), (100, 100))
                    P2_rect.center = P2.x, P2.y
                    if P2_rect.colliderect(par.hit_box) and not par.hit:
                        par.hit = True
                        if par.speed != 1:
                            P1.projectiles.remove(par)
                        P2.health -= int(par.dmg * P2.income_dmg_multiplier)
                        if P2.health <= 0:
                            Ps.remove(P2)


def show_mob_health(M: mob.Mob):
    pygame.draw.rect(screen, (0, 255, 0), ((M.x - 50, M.y - 70), (M.health // M.lvl, 10)))
    pygame.draw.rect(screen, (255, 0, 0), ((M.x - 50 + M.health // M.lvl, M.y - 70), (100 - M.health // M.lvl, 10)))


def show_player_health(P: player.Player):
    pygame.draw.rect(screen, (0, 255, 0), ((P.x - 50, P.y - 70), (P.health, 10)))
    pygame.draw.rect(screen, (255, 0, 0), ((P.x - 50 + P.health, P.y - 70), (100 - P.health, 10)))


def show_mob_lvl(M: mob.Mob):
    name = font.render(str(M.lvl), True, (0, 0, 0))
    name_rect = name.get_rect()
    name_rect.center = M.x, M.y
    name_rect.y -= 70
    name_rect.x -= 70
    screen.blit(name, name_rect)


def show_name(P: player.Player):
    name = font.render(P.nickname, True, (0, 0, 0))
    name_rect = name.get_rect()
    name_rect.center = P.x, P.y
    name_rect.y -= 90
    screen.blit(name, name_rect)


def main():
    CL = pygame.time.Clock()
    P = player.Player("Hunnydrips", 0, 0)
    P2 = player.Player("Glidaria", 0, 0)
    P_rect = pygame.Rect((0, 0), (100, 100))
    M = mob.Mob(50, 50, 5)
    M2 = mob.Mob(500, 50, 3)
    M_rect = pygame.Rect((0, 0), (100, 100))
    players = [P, P2]
    mobs = [M, M2]
    running = True
    while running:
        screen.fill((0, 0, 255))
        m_x, m_y = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    P.use_ability()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    P.attack(m_x, m_y)
                elif event.button == 3:
                    P2.attack(m_x, m_y)
        keys = pygame.key.get_pressed()
        P.dir_x = keys[pygame.K_d] - keys[pygame.K_a]
        P.dir_y = keys[pygame.K_s] - keys[pygame.K_w]
        P2.dir_x = keys[pygame.K_l] - keys[pygame.K_j]
        P2.dir_y = keys[pygame.K_k] - keys[pygame.K_i]
        for Pl in players:
            Pl.move()
            Pl.ability()
            P_rect.center = Pl.x, Pl.y
            pygame.draw.rect(screen, (0, 255, 0), P_rect)
            show_player_health(Pl)
            show_name(Pl)
            for par in Pl.projectiles:
                if par.range <= 0:
                    Pl.projectiles.remove(par)
                par.move()
                pygame.draw.rect(screen, (255, 0, 0), par.hit_box)
        for Mo in mobs:
            if Mo.is_alive:
                Mo.move(players)
                M_rect.center = Mo.x, Mo.y
                pygame.draw.rect(screen, (0, 255, 0), M_rect)
                show_mob_lvl(Mo)
                show_mob_health(Mo)
            elif time.time() - Mo.death_time >= 7:
                Mo.is_alive = True
                Mo.x, Mo.y = Mo.home_x, Mo.home_y
                Mo.health = 100 * Mo.lvl
            for spear in Mo.spears:
                if spear.range <= 0:
                    Mo.spears.remove(spear)
                spear.move()
                pygame.draw.rect(screen, (255, 0, 0), spear.hit_box)
        identify_par_dmg(players, mobs)
        draw_gold(P.gold)
        CL.tick(60)
        pygame.display.update()
        # cringe


if __name__ == '__main__':
    main()
