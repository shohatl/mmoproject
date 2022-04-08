from Classes import mob, player, particle
import pygame


def build_mobs_list(mobs: list, P: player.Player):
    M_rect = pygame.Rect((0, 0), (100, 100))
    P_screen_rect = pygame.Rect((0, 0), (1920, 1080))
    P_screen_rect.center = P.x, P.y
    for M in mobs:
        M_rect.center = M.x, M.y
        if M in P.mobs_on_screen and not M_rect.colliderect(P_screen_rect):
            P.mobs_on_screen.remove(M)
        elif M_rect.colliderect(P_screen_rect) and M_rect not in P.mobs_on_screen:
            P.mobs_on_screen.append(M)
        for par in M.spears:
            if par in P.particles_on_screen and not P_screen_rect.colliderect(par.hit_box):
                P.particles_on_screen.remove(par)
            elif P_screen_rect.colliderect(par.hit_box) and par not in P.particles_on_screen:
                P.particles_on_screen.append(par)


def build_players_list(players: list, P: player.Player):
    P2_rect = pygame.Rect((0, 0), (100, 100))
    P_screen_rect = pygame.Rect((0, 0), (1920, 1080))
    P_screen_rect.center = P.x, P.y
    for P2 in players:
        P2_rect.center = P2.x, P2.y
        if P2 in P.mobs_on_screen and not P2_rect.colliderect(P_screen_rect):
            P.mobs_on_screen.remove(P2)
        elif P2_rect.colliderect(P_screen_rect) and P2_rect not in P.mobs_on_screen:
            P.mobs_on_screen.append(P2)
        for par in P2.projectiles:
            if par in P.particles_on_screen and not P_screen_rect.colliderect(par.hit_box):
                P.particles_on_screen.remove(par)
            elif P_screen_rect.colliderect(par.hit_box) and par not in P.particles_on_screen:
                P.particles_on_screen.append(par)




