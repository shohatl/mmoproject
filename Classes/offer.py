import pygame

from Classes import button

buy = pygame.image.load("../Assets/shop/buy.png")
upgrade = pygame.image.load("../Assets/shop/upgrade.png")
sell = pygame.image.load("../Assets/shop/sell.png")
offer_surface = pygame.image.load("../Assets/shop/offer.png")


class Offer:
    def __init__(self, sort, item):
        self.sort = sort
        self.buttons = []
        self.item = item
        if self.sort == "buy":
            self.buttons.append(button.Button(100, 100, buy))
        else:
            self.buttons.append(button.Button(100, 200, upgrade))
            self.buttons.append(button.Button(100, 200, sell))

    def show_offer(self, screen):
        screen.blit(offer_surface, (0, 0))
        for B in self.buttons:
            B.show_button(screen)
            if B.check_press():
                if len(self.buttons) == 1:
                    print("bye button")
                elif B.y == 100:
                    print("upgrade pressed")
                else:
                    print("sell pressed")
