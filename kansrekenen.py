import random

class Players:
    def __init__(self):
        self.cards = []
        self.points = 0
        self.amount_of_aces = 0
        self.add_points()

    def get_card(self, card):
        self.cards.append(card)
        self.add_points()

    def add_points(self):
        points = 0
        amount_of_aces = 0
        for card in self.cards:
            if card[1] < 11 and 1 < card[1]:
                points += card[1]

            elif card[1] == 1:
                amount_of_aces += 1
                points += 11
            else:
                points += 10
        self.points = points
        self.amount_of_aces = amount_of_aces
        self.total_points()

    def total_points(self):
        if self.points > 21:
            if self.amount_of_aces > 0:
                self.points -= 10
                self.amount_of_aces -= 1
                self.total_points()

    def status(self):
        return self.cards, self.points

    colors = ["h", "d", "c", "s"]
    Waarde = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]

    cards = {(color, value) for color in colors for value in Waarde}
    deleted_cards = []

    def random_card_choice(cards, deleted_cards):
        random_cards = random.choice(list(cards))
        cards.remove(random_cards)
        deleted_cards.append(random_cards)
        return random_cards

    def hit(player, cards, deleted_cards):
        # in class when code is done
        player.get_card(random_card_choice(cards, deleted_cards))

    def double(player, cards, deleted_cards):
        # in class when code is done
        player.get_card(random_card_choice(cards, deleted_cards))

def value_card(card):
    if card[1] < 11 and 1 < card[1]:
        return card[1]
    elif card[1] == 1:
        return 1
    else:
        return 10

def kans_sucess_stand(player_cards,dealer_cards,player_point,dealer_point,cards):
    card_dict = dict()
    for card in list(cards):
        if card[1] not in card_dict:
            card_dict[card[1]] = 1
        else:
            card_dict[card[1]] = card_dict[card[1]] + 1
    if player_point > 21:
        return 0
    elif player_point==21:
        return 100
    elif player_point < 17:


















