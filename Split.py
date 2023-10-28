import random

class Players:
    def __init__(self):
        self.hands = [Hand()]

    def can_split(self):
        card1, card2 = self.hands[0].cards
        if len(self.hands) == 1 and point_of_card(card1) == point_of_card(card2):
            return True
        else:
            return False

    def split(self):
        if self.can_split():
            card1, card2 = self.hands[0].cards
            self.hands = [Hand([card1]), Hand([card2])]

    def get_card(self, card, hand_idx=0):
        self.hands[hand_idx].cards.append(card)
        self.hands[hand_idx].add_points()

    def status(self):
        return [[hand.cards, hand.points] for hand in self.hands]


class Hand:
    def __init__(self, cards=None):
        self.cards = cards if cards else []
        self.points = 0
        self.amount_of_aces = 0
        self.add_points()

    def add_points(self):
        points = 0
        for card in self.cards:
            if card[1] > 1 and card[1] < 11:
                points += card[1]
            elif card[1] == 1:
                points += 11
            else:
                points += 10
        self.points = points



def point_of_card(card):
    if card[1] > 1 and card[1] < 11:
        value = card[1]
    elif card[1] == 1:
        value = 1
    else:
        value = 10
    return value


colors = ["Heart", "Diamonds", "Clubs", "Spades"]
Waarde = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 1]

cards = {(color, value) for color in colors for value in Waarde}
deleted_cards = []


def random_card_choice(cards, deleted_cards):
    random_cards = random.choice(list(cards))
    cards.remove(random_cards)
    deleted_cards.append(random_cards)
    return random_cards


def hit(player, cards, deleted_cards, hand_index):
    # in class when code is done
    player.get_card(random_card_choice(cards, deleted_cards), hand_index)


def double(player, cards, deleted_cards, hand_index):
    # in class when code is done
    player.get_card(random_card_choice(cards, deleted_cards), hand_index)
    # money double


response = input("Do you want to play the game(y/n): ")
if response == "y":
    run = True
    number_of_player = int(input("How much players (max 7):  "))
else:
    run = False
while run:
    # gives cards to the players
    Player1 = Players()
    Player2 = Players()
    Player3 = Players()
    Player4 = Players()
    Player5 = Players()
    Player6 = Players()
    Player7 = Players()
    max_players = [Player1, Player2, Player3, Player4, Player5, Player6, Player7]
    players = []
    for i in range(1, number_of_player + 1):
        players.append(max_players[i - 1])
    for number in range(len(players)):
        players[number].get_card(random_card_choice(cards, deleted_cards))
        players[number].get_card(random_card_choice(cards, deleted_cards))
        player_status = players[number].status()[0]
        if player_status[1] == 21:
            print(
                "Player" + str(number + 1),
                "has:",
                player_status[0],
                "as cards and:",
                player_status[1],
                "points, BLACK JACK !!.",
            )
        else:
            print(
                "Player" + str(number + 1),
                "has:",
                player_status[0],
                "as cards and:",
                player_status[1],
                "points.",
            )

    # gives cards to the dealer
    dealer = Players()
    dealer.get_card(random_card_choice(cards, deleted_cards))

    print("Dealer receive a card, you don't know the value")
    dealer.get_card(random_card_choice(cards, deleted_cards))
    print("Dealer receive another card:", dealer.status()[0][0][1])

    # ask for the move
    busted_player = []
    for number in range(1, number_of_player + 1):
        print("Player" + str(number) + "'s", "turn")
        if players[number - 1].can_split():
            split_move = input("Do you want to split (y/n)?")
            if split_move == "y":
                players[number - 1].split()
                players[number - 1].get_card(
                    random_card_choice(cards, deleted_cards), 0
                )
                print(
                    "first hand:",
                    players[number - 1].status()[0][0],
                    "points:",
                    players[number - 1].status()[0][1],
                )
                players[number - 1].get_card(
                    random_card_choice(cards, deleted_cards), 1
                )
                print(
                    "second hand:",
                    players[number - 1].status()[1][0],
                    "points:",
                    players[number - 1].status()[1][1],
                )
            else:
                pass
        for hand_index in range(len(players[number - 1].status())):
            hand = players[number - 1].status()[hand_index]
            if hand_index > 0:
                print(str(hand_index + 1) + "de hand : ")
            print(
                "Your cards:",
                players[number - 1].status()[hand_index][0],
                "and points:",
                players[number - 1].status()[hand_index][1],
            )
            move = int(
                input("Wich move do you want to do ? Hit (1), double (2), stand(3) ")
            )
            if move == 1:
                run_hit = True
                while run_hit:
                    hit(players[number - 1], cards, deleted_cards, hand_index)
                    player_status = players[number - 1].status()[hand_index]
                    print(
                        "You have",
                        player_status[0],
                        "as cards and:",
                        player_status[1],
                        "points.",
                    )
                    if player_status[1] > 21:
                        print("You are busted !")
                        busted_player.append(players[number - 1])
                        run_hit = False
                    else:
                        still_hit = int(input("Hit again(1) or stand(2) ? "))
                        if still_hit == 1:
                            run_hit = True
                        else:
                            run_hit = False
            elif move == 2:
                double(players[number - 1], cards, deleted_cards, hand_index)
                player_status = players[number - 1].status()[hand_index]
                print(
                    "You have",
                    player_status[0],
                    "as cards and:",
                    player_status[1],
                    "points.",
                )
                if player_status[1] > 21:
                    print("You are busted !")
                    busted_player.append(players[number - 1])
                else:
                    pass
            else:
                pass
    # delete busted players
    # Dealer game
    print("Dealer's turn !")
    dealer_takes_card = True
    dealer_busted = False
    while dealer_takes_card:
        dealer_score = dealer.status()[0][1]
        print(
            "Dealer's card are",
            dealer.status()[0][0],
            "with a score of :",
            dealer_score,
            "points.",
        )
        if dealer_score > 21:
            print("Dealer busted. All the players won !!")
            dealer_busted = True
            dealer_takes_card = False
        elif dealer_score >= 17:
            dealer_takes_card = False
        else:
            print("Dealer takes a new card")
            dealer.get_card(random_card_choice(cards, deleted_cards))
    # Score players
    if dealer_busted == False:
        for number in range(0, len(players)):
            for hand_index in range(len(players[number].status())):
                hand = players[number].status()[hand_index]
                if hand_index > 0:
                    print(str(hand_index + 1) + "de hand : ")
                if players[number] in busted_player:
                    if hand_index > 0:
                        print("Second hand busted")
                    else:
                        print("Player" + str(number + 1), "busted")
                elif players[number].status()[hand_index][1] > dealer_score:
                    print(
                        "Player " + str(number + 1),
                        "won with a score of",
                        players[number].status()[hand_index][1],
                        "points.",
                    )
                elif players[number].status()[hand_index][1] == dealer_score:
                    print(
                        "Push. Player " + str(number + 1),
                        "has same score as the dealer",
                    )
                else:
                    print(
                        "Player " + str(number + 1),
                        "lose with a score of",
                        players[number].status()[hand_index][1],
                        "points.",
                    )

    # end of the game

    # Réinsérer les cartes retirées dans le set de base
    cards.update((deleted_cards))
    response = input("Do you still wanna play(y/n)")
    if response == "y":
        run = True
        number_of_player = int(input("How much players:  "))
    else:
        run = False
