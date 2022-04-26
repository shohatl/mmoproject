import random
import secrets
import pygame

screen = pygame.display.set_mode((500, 500))
river = []
pot = 0


def generate_card():
    x = secrets.randbelow(4)
    card_kind = 'clover'
    if x == 0:
        card_kind = 'spade'
    elif x == 1:
        card_kind = 'heart'
    elif x == 2:
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
        self.choice = ''
        self.bet = 0
        # 110402


def print_all_cards_dealt(players: list):
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


def winner_check(ps: list, flop_list: list):
    print(flop_list)
    print(ps)
    pass


def give_straight_flush_points(cards_of_player: list, flop_list: list):
    pass


def give_flush_rank(cards_of_player: list, flop_list: list):
    highest_spade = 0
    highest_diamond = 0
    highest_clover = 0
    highest_heart = 0
    amount_of_spades_in_flop = 0
    amount_of_hearts_in_flop = 0
    amount_of_diamonds_in_flop = 0
    amount_of_clovers_in_flop = 0
    for card in flop_list:
        if card.card_kind == 'spade':
            amount_of_spades_in_flop += 1
            highest_spade = highest_spade * int(highest_spade > card.card_number) + card.card_number * int(
                highest_spade < card.card_number)
            highest_spade = int(card.card_number == 1) * 14 + int(card.card_number != 1) * highest_spade
        elif card.card_kind == 'heart':
            amount_of_hearts_in_flop += 1
            highest_heart = highest_heart * int(highest_heart > card.card_number) + card.card_number * int(
                highest_heart < card.card_number)
            highest_heart = int(card.card_number == 1) * 14 + int(card.card_number != 1) * highest_heart
        elif card.card_kind == 'clover':
            amount_of_clovers_in_flop += 1
            highest_clover = highest_clover * int(highest_clover > card.card_number) + card.card_number * int(
                highest_clover < card.card_number)
            highest_clover = int(card.card_number == 1) * 14 + int(card.card_number != 1) * highest_clover
        else:
            amount_of_diamonds_in_flop += 1
            highest_diamond = highest_diamond * int(highest_diamond > card.card_number) + card.card_number * int(
                highest_diamond < card.card_number)
            highest_diamond = int(card.card_number == 1) * 14 + int(card.card_number != 1) * highest_diamond

    amount_of_spades_in_player = 0
    amount_of_hearts_in_player = 0
    amount_of_diamonds_in_player = 0
    amount_of_clovers_in_player = 0
    for card in cards_of_player:
        if card.card_kind == 'spade':
            amount_of_spades_in_player += 1
            highest_spade = highest_spade * int(highest_spade > card.card_number) + card.card_number * int(
                highest_spade < card.card_number)
            highest_spade = int(card.card_number == 1) * 14 + int(card.card_number != 1) * highest_spade
        elif card.card_kind == 'heart':
            amount_of_hearts_in_player += 1
            highest_heart = highest_heart * int(highest_heart > card.card_number) + card.card_number * int(
                highest_heart < card.card_number)
            highest_heart = int(card.card_number == 1) * 14 + int(card.card_number != 1) * highest_heart
        elif card.card_kind == 'clover':
            amount_of_clovers_in_player += 1
            highest_clover = highest_clover * int(highest_clover > card.card_number) + card.card_number * int(
                highest_clover < card.card_number)
            highest_clover = int(card.card_number == 1) * 14 + int(card.card_number != 1) * highest_clover
        else:
            amount_of_diamonds_in_player += 1
            highest_diamond = highest_diamond * int(highest_diamond > card.card_number) + card.card_number * int(
                highest_diamond < card.card_number)
            highest_diamond = int(card.card_number == 1) * 14 + int(card.card_number != 1) * highest_diamond
    # todo: add a right calc of vale that represents the rank according to my table

    if amount_of_clovers_in_player and amount_of_clovers_in_flop + amount_of_clovers_in_player > 4:
        # there is flush
        print('flash')
        print(highest_clover + 67)
    elif amount_of_hearts_in_player and amount_of_hearts_in_flop + amount_of_hearts_in_player > 4:
        # there is flush
        print('flash')
        print(highest_heart + 67)
    elif amount_of_spades_in_player and amount_of_spades_in_flop + amount_of_spades_in_player > 4:
        # there is flush
        print('flash')
        print(highest_spade + 67)
    elif amount_of_diamonds_in_player and amount_of_diamonds_in_flop + amount_of_diamonds_in_player > 4:
        # there is flush
        print('flash')
        print(highest_diamond + 67)
    else:
        print('no flush')
        return


def main():
    Ps = []
    for i in range(5):
        Ps.append(Player())
    alr_used = deal_to_players(Ps)
    print_all_cards_dealt(Ps)
    print('=======================================')
    flop_list = []
    while True:
        screen.fill((10, 48, 18))
        for i, C in enumerate(flop_list):
            img = pygame.transform.scale(
                pygame.image.load(f'{C.card_number}, {C.card_kind}.png'), (70, 100))
            screen.blit(img, (100 * i, 250))
        # C = flop_list_1[0]
        # img = pygame.transform.scale(pygame.image.load(f'{C.card_number}, {C.card_kind}.png'), (70, 100))
        # screen.blit(img, (300, 250))
        # C = flop_list_2[0]
        # img = pygame.transform.scale(pygame.image.load(f'{C.card_number}, {C.card_kind}.png'), (70, 100))
        # screen.blit(img, (400, 250))
        for i, P in enumerate(Ps):
            x = 0
            for k in range(2):
                img = pygame.transform.scale(pygame.image.load(f'{P.cards[k].card_number}, {P.cards[k].card_kind}.png'),
                                             (70, 100))
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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not flop_list:
                        flop_list, alr_used = flop(alr_used, 3)
                    elif len(flop_list) < 5:
                        flop_list_1, alr_used = flop(alr_used, 1)
                        flop_list.extend(flop_list_1)
                    else:
                        for p in Ps:
                            give_flush_rank(p.cards, flop_list)


if __name__ == '__main__':
    main()
