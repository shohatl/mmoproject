import random
import pygame

screen = pygame.display.set_mode((500, 500))
river = []
pot = 0


def generate_card():
    x = random.randint(0, 5)
    card_kind = 'clover'
    if x == 0:
        card_kind = 'spade'
    elif x == 1:
        card_kind = 'heart'
    elif x == 0:
        card_kind = 'diamond'
    card_number = random.randint(1, 13)
    card_for_return = Card(card_kind=card_kind, card_number=card_number)
    return card_for_return


class Card:
    def __init__(self, card_kind: str, card_number: int):
        self.card_kind = card_kind
        self.card_number = card_number


class Player:
    def __init__(self):
        self.cards = []
        self.choise = ''
        self.bet = 0


def print_all_cards_dealed(players: list):
    for P in players:
        print('================================')
        for i in range(2):
            print(f'{P.cards[i].card_number}, {P.cards[i].card_kind}')


def deal_to_players(p_list: list):
    generated_cards = []
    for P in p_list:
        i = 0
        while i < 2:
            card_for_try = generate_card()
            if contains(generated_cards, card_for_try):
                generated_cards.append(card_for_try)
                P.cards.append(card_for_try)
                i += 1
    return generated_cards


def contains(cards: list, card: Card):
    for cardI in cards:
        if cardI.card_number == card.card_number and cardI.card_kind == card.card_kind:
            return False
    return True


def flop(alr_used: list, amount: int):
    flop_list = []
    i = 0
    while i < amount:
        card_for_try = generate_card()
        if contains(alr_used, card_for_try):
            flop_list.append(card_for_try)
            alr_used.append(card_for_try)
            print(f'{card_for_try.card_number}, {card_for_try.card_kind}')
            i += 1
    return flop_list, alr_used


def main():
    card_blank = pygame.image.load('card_blank.png')
    Ps = []
    for i in range(5):
        Ps.append(Player())
    alr_used = deal_to_players(Ps)
    print_all_cards_dealed(Ps)
    print('=======================================')
    flop(alr_used, 3)
    print('----------------------')
    flop(alr_used, 1)
    print('----------------------')
    flop(alr_used, 1)
    while True:
        screen.fill((10, 48, 18))
        for i, P in enumerate(Ps):
            x = 0
            for k in range(2):
                img = card_blank
                try:

                    img = pygame.transform.scale(
                        pygame.image.load(f'{P.cards[k].card_number}, {P.cards[k].card_kind}.png'), (70, 100))
                except:
                    pass
                if i == 0:
                    screen.blit(img, (0 + x, 405))
                if i == 1:
                    screen.blit(img, (0 + x, 0))
                if i == 2:
                    screen.blit(img, (200 + x, 0))
                if i == 3:
                    screen.blit(img, (416 + x, 0))
                if i == 4:
                    screen.blit(img, (416 + x, 405))
                x += 20

            pass
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.exit()


if __name__ == '__main__':
    main()
