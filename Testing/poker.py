import random
import secrets
import sys

import pygame
import numpy

screen = pygame.display.set_mode((500, 500))
river = []
pot = 0


def get_full_house_rank(cards_of_player: list, flop_list: list):
    if cards_of_player[0].card_number == cards_of_player[1].card_number:
        # gotta check if the table has free of a kind or makes me have 3 of a kind + has a parir
        amount_of_my_card = 2
        for c in flop_list:
            if c.card_number == cards_of_player[0].card_number:
                amount_of_my_card = 3
        for i in range(3):
            num = flop_list[i].card_number
            amount = 1
            for k in range(i + 1, 5):
                if flop_list[k].card_number == num:
                    amount += 1
            if num == 1:
                num = 14
            num2 = cards_of_player[0].card_number
            if num2 == 1:
                num2 = 14
            if amount == 3:
                return 50 * num + num2
            elif amount == 2 and amount_of_my_card == 3:
                return 50 * num2 + num
    else:
        amount_of_first_card = 1
        amount_of_second_card = 1
        num1 = cards_of_player[0].card_number
        num2 = cards_of_player[1].card_number
        if num1 == 1:
            num1 = 14
        if num2 == 1:
            num2 = 14
        for c in flop_list:
            if c.card_number == cards_of_player[0].card_number:
                amount_of_first_card += 1
            elif c.card_number == cards_of_player[1].card_number:
                amount_of_second_card += 1
        if amount_of_second_card > 2 and amount_of_first_card > 2:
            if num1 > num2:
                return num1 * 50 + num2
            else:
                return num2 * 50 + num1
        if amount_of_first_card == 3 and amount_of_second_card == 2:
            return num1 * 50 + num2
        if amount_of_first_card == 2 and amount_of_second_card == 3:
            return num2 * 50 + num1
        if amount_of_first_card == 3:
            for i, c in enumerate(flop_list):
                if c.card_number != num1:
                    other_num = c.card_number
                    for k in range(i + 1, 5):
                        if flop_list[k].card_number == other_num:
                            return num1 * 50 + other_num
        if amount_of_second_card == 3:
            for i, c in enumerate(flop_list):
                if c.card_number != num2:
                    other_num = c.card_number
                    for k in range(i + 1, 5):
                        if flop_list[k].card_number == other_num:
                            return num2 * 50 + other_num
        if amount_of_first_card == 2:
            for i, c in enumerate(flop_list):
                if c.card_number != num1:
                    other_amount = 1
                    other_num = c.card_number
                    for k in range(i + 1, 5):
                        if flop_list[k].card_number == other_num:
                            other_amount += 1
                            if other_amount == 3:
                                return other_num * 50 + num1
        if amount_of_second_card == 2:
            for i, c in enumerate(flop_list):
                if c.card_number != num2:
                    other_amount = 1
                    other_num = c.card_number
                    for k in range(i + 1, 5):
                        if flop_list[k].card_number == other_num:
                            other_amount += 1
                            if other_amount == 3:
                                return other_num * 50 + num2
    return 0


def get_rank_of_free_of_a_kind(cards_of_player: list, flop_list: list):
    if cards_of_player[0].card_number == cards_of_player[1].card_number:
        num = cards_of_player[0].card_number
        amount = 0
        for C2 in flop_list:
            if num == C2.card_number:
                amount += 1
        if num == 1:
            num = 14
        if amount == 1:
            return num + 35
        elif amount == 2:
            return num + 712
        return 0
    for C in cards_of_player:
        amount_of_first = 0
        num = C.card_number
        for C2 in flop_list:
            if C2.card_number == num:
                amount_of_first += 1
        if num == 1:
            num = 14
        if amount_of_first == 2:
            return num + 35
        elif amount_of_first == 3:
            return num + 712  # 4 of a kind

    return 0


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

    def __repr__(self):
        return f'{self.card_number}'


class Player:
    def __init__(self):
        self.cards = []
        self.choice = ''
        self.bet = 0
        self.hand_rank = 0
        # 110402


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
            i += 1
    return flop_list, alr_used


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

    if amount_of_clovers_in_player and amount_of_clovers_in_flop + amount_of_clovers_in_player > 4:
        # there is flush
        return highest_clover + 53
    elif amount_of_hearts_in_player and amount_of_hearts_in_flop + amount_of_hearts_in_player > 4:
        # there is flush
        return highest_heart + 53
    elif amount_of_spades_in_player and amount_of_spades_in_flop + amount_of_spades_in_player > 4:
        # there is flush
        return highest_spade + 53
    elif amount_of_diamonds_in_player and amount_of_diamonds_in_flop + amount_of_diamonds_in_player > 4:
        # there is flush
        return highest_diamond + 53
    else:
        return 0


def get_pair_rank(cards_of_player: list, flop_list: list):
    pair_num = 0
    amount_of_pairs = 0
    if len(cards_of_player) == 2:
        if cards_of_player[0].card_number == cards_of_player[1].card_number:
            amount_of_pairs = 1
            pair_num = cards_of_player[1].card_number
    for card in cards_of_player:
        for card_on_river in flop_list:
            if card_on_river.card_number == card.card_number:
                amount_of_pairs += 1
                pair_num = card_on_river.card_number

    if amount_of_pairs > 1 or amount_of_pairs == 0:
        return 0
    if pair_num == 1:
        pair_num = 14
    return 10 + pair_num


def get_two_pair_rank(cards_of_player: list, flop_list: list):
    if cards_of_player[0].card_number == cards_of_player[1].card_number:
        return 0
    first_card_as_a_list = [cards_of_player[0]]
    second_card_as_a_list = [cards_of_player[1]]
    rank_of_first_pair = get_pair_rank(first_card_as_a_list, flop_list)
    rank_of_second_pair = get_pair_rank(second_card_as_a_list, flop_list)
    if rank_of_first_pair and rank_of_second_pair:
        if rank_of_first_pair > rank_of_second_pair:
            return rank_of_first_pair + 12
        return rank_of_second_pair + 12
    return 0


def get_high_hand_rank(cards_of_player: list):
    if cards_of_player[0].card_number == 1 or cards_of_player[1].card_number == 1:
        return 11
    if cards_of_player[0].card_number > cards_of_player[1].card_number:
        return cards_of_player[0].card_number - 3
    return cards_of_player[1].card_number - 3


def add_to_list(list_sorted: list, card: Card):
    if not list_sorted:
        return [card]
    if list_sorted[-1].card_number <= card.card_number:
        list_sorted.append(card)
        return list_sorted
    if list_sorted[0].card_number >= card.card_number:
        new_list = [card]
        new_list.extend(list_sorted)
        return new_list
    for i in range(len(list_sorted)):
        if list_sorted[i].card_number < card.card_number <= list_sorted[i + 1].card_number:
            new_list = list_sorted[:i + 1]
            new_list.append(card)
            new_list.extend(list_sorted[i + 1:])
            return new_list


def get_straight_rank(cards_of_player: list, flop_list: list):
    sorted_list = []
    for c in flop_list:
        sorted_list = add_to_list(sorted_list, c)
    print(sorted_list)
    following = 1
    for i in range(len(sorted_list) - 1):
        if sorted_list[i].card_number + 1 == sorted_list[i + 1].card_number:
            following += 1
            if following == 4 and sorted_list[i + 1].card_number == 13 and sorted_list[0].card_number == 1:
                print('straight')
            if following == 5:
                print('straight')
        elif sorted_list[i] != sorted_list[i + 1]:
            following = 1
    return 0


def main():
    Ps = []
    for i in range(5):
        Ps.append(Player())
    alr_used = deal_to_players(Ps)
    # Ps[0].cards[0].card_number = 2
    # Ps[0].cards[1].card_number = 1
    print('=======================================')
    flop_list = []
    while True:
        screen.fill((10, 48, 18))
        for i, C in enumerate(flop_list):
            img = pygame.transform.scale(
                pygame.image.load(f'{C.card_number}, {C.card_kind}.png'), (70, 100))
            screen.blit(img, (100 * i + 15, 200))
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

            pass#
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not flop_list:
                        flop_list, alr_used = flop(alr_used, 3)
                        flop_list[0].card_number = 13
                        flop_list[1].card_number = 1
                        flop_list[2].card_number = 12
                    elif len(flop_list) < 5:
                        flop_list_1, alr_used = flop(alr_used, 1)
                        flop_list.extend(flop_list_1)
                        flop_list[3].card_number = 11
                    else:
                        for p in Ps:
                            ranks = [give_flush_rank(p.cards, flop_list), get_rank_of_free_of_a_kind(p.cards,
                                                                                                     flop_list),
                                     get_two_pair_rank(p.cards, flop_list), (get_pair_rank(p.cards, flop_list)),
                                     get_high_hand_rank(p.cards), get_full_house_rank(p.cards, flop_list)]
                            p.hand_rank = numpy.max(ranks)
                            # print(p.hand_rank)
                        print('-----------------')
                        get_straight_rank([], flop_list)


if __name__ == '__main__':
    main()
