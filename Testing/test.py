import pygame
import sys
from Classes import player, mob


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    CL = pygame.time.Clock()
    P = player.Player("Hunnydrips", 0, 0)
    P_rect = pygame.Rect((0, 0), (100, 100))
    M = mob.Mob(50, 50, 5)
    M_rect = pygame.Rect((0, 0), (100, 100))
    running = True
    while running:
        screen.fill((0, 0, 255))
        m_x, m_y = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                P.attack(m_x, m_y)
        keys = pygame.key.get_pressed()
        P.dir_x = keys[pygame.K_d] - keys[pygame.K_a]
        P.dir_y = keys[pygame.K_s] - keys[pygame.K_w]
        P.move()
        P_rect.center = P.x, P.y
        players = [P]
        M.move(players)
        M_rect.center = M.x, M.y
        pygame.draw.rect(screen, (0, 255, 0), P_rect)
        pygame.draw.rect(screen, (0, 255, 0), M_rect)
        _ = P.inventory[P.picked]
        for par in P.projectiles:
            if par.range <= 0:
                P.projectiles.remove(par)
            par.move()
            pygame.draw.rect(screen, (255, 0, 0), par.hit_box)
        for spear in M.spears:
            if spear.range <= 0:
                M.spears.remove(spear)
            spear.move()
            pygame.draw.rect(screen, (255, 0, 0), spear.hit_box)
        CL.tick(60)
        pygame.display.update()


if __name__ == '__main__':
    main()
