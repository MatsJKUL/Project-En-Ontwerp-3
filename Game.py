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
            if type(card[1]) is int:
                points += card[1]

            elif card[1] == "ace":
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


colors = ["Heart", "Diamonds", "Clubs", "Spades"]
Waarde = [2, 3, 4, 5, 6, 7, 8, 9, 10, "Jack", "Queen", "King", "Ace"]

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
    # money double


response = input("Do you want to play the game(y/n): ")
if response == "y":
    run = True
    number_of_player = int(input("How much players:  "))
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
        player_status = players[number].status()
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
    cards_dealer = []
    cards_dealer.append(random_card_choice(cards, deleted_cards))

    print("Dealer receive a card, you don't know the value")
    cards_dealer.append(random_card_choice(cards, deleted_cards))
    print("Dealer receive another card:", cards_dealer[1])

    # ask for the move
    for number in range(1, number_of_player + 1):
        print("Player" + str(number) + "'s", "turn")
        move = int(
            input("Wich move do you want to do ? Hit (1), double (2), stand(3) ")
        )
        if move == 1:
            run_hit = True
            while run_hit:
                hit(players[number - 1], cards, deleted_cards)
                player_status = players[number - 1].status()
                print(
                    "You have",
                    player_status[0],
                    "as cards and:",
                    player_status[1],
                    "points.",
                )
                if player_status[1] > 21:
                    print("You are busted !")
                    players.remove(players[number - 1])
                    run_hit = False
                else:
                    still_hit = int(input("Hit again(1) or stand(2) ? "))
                    if still_hit == 1:
                        run_hit = True
                    else:
                        run_hit = False
        elif move == 2:
            double(players[number - 1], cards, deleted_cards)
            player_status = players[number - 1].status()
            print(
                "You have",
                player_status[0],
                "as cards and:",
                player_status[1],
                "points.",
            )
            if player_status[1] > 21:
                print("You are busted !")
                players.remove(players[number - 1])
            else:
                still_hit = int(input("Hit again(1) or stand(2) ? "))
            # give cards + score with code class
        else:
            pass

    # end of the game

    # Réinsérer les cartes retirées dans le set de base
    cards.update((deleted_cards))
    response = input("Do you still wanna play(y/n)")
    if response == "y":
        run = True
        number_of_player = input("How much players:  ")
    else:
        run = False
