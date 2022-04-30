from Classes import mob, player, particle
import pygame


def build_mobs_list(mobs: list, P: player.Player):
    M_rect = pygame.Rect((0, 0), (100, 100))
    P_screen_rect = pygame.Rect((0, 0), (1920, 1080))
    P_screen_rect.center = P.x, P.y
    list_to_be_sent = []
    list_to_tell_to_remove = []
    particles_to_remove = []
    for M in mobs:
        M_rect.center = M.x, M.y
        if M.is_alive:
            if M_rect.colliderect(P_screen_rect) and (M.has_moved or M not in P.mobs_on_screen):
                list_to_be_sent.append(M)
                if M not in P.mobs_on_screen:
                    P.mobs_on_screen.append(M)
            elif not M_rect.colliderect(P_screen_rect) and M in P.mobs_on_screen:
                list_to_tell_to_remove.append(M)
                P.mobs_on_screen.remove(M)
        for par in M.projectiles:
            if par in P.particles_on_screen and not P_screen_rect.colliderect(par.hit_box):
                P.particles_on_screen.remove(par)
                particles_to_remove.append(par)
            elif P_screen_rect.colliderect(par.hit_box) and par not in P.particles_on_screen:
                P.particles_on_screen.append(par)
    return list_to_be_sent, list_to_tell_to_remove, particles_to_remove


def build_players_list(players: list, P: player.Player):
    P2_rect = pygame.Rect((0, 0), (100, 100))
    P_screen_rect = pygame.Rect((0, 0), (1920, 1080))
    P_screen_rect.center = P.x, P.y
    list_to_be_sent = []
    list_to_tell_to_remove = []
    particles_to_remove = []
    for P2 in players:
        if P2.nickname != P.nickname:
            P2_rect.center = P2.x, P2.y
            if P2_rect.colliderect(P_screen_rect) and (P2.has_moved or P2 not in P.other_players_list):
                list_to_be_sent.append(P2)
                if P2 not in P.other_players_list:
                    P.other_players_list.append(P2)
            elif not P2_rect.colliderect(P_screen_rect) and P2 in P.other_players_list:
                list_to_tell_to_remove.append(P2)
                P.mobs_on_screen.remove(P2)
        for par in P2.projectiles:
            if par in P.particles_on_screen and not P_screen_rect.colliderect(par.hit_box):
                P.particles_on_screen.remove(par)
                particles_to_remove.append(par)
            elif P_screen_rect.colliderect(par.hit_box) and par not in P.particles_on_screen:
                P.particles_on_screen.append(par)
    return list_to_be_sent, list_to_tell_to_remove, particles_to_remove
