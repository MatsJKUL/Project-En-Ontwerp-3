import random

colors = ["Heart", "diamonds", "clubs", "spades"]
Waarde = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"]

cards = {(color, value) for color in colors for value in Waarde}
deleted_cards = []

def random_card_choice(cards,deleted_cards):
    random_cards = random.choice(list(cards))
    cards.remove(random_cards)
    deleted_cards.append(random_cards)
    return random_cards

def hint(cards_player,number,cards,deleted_cards):
    # in class when code is done
    cards_player.append(random_card_choice(cards, deleted_cards))

def double(cards_player,number,cards,deleted_cards):
    #in class when code is done
    cards_player.append(random_card_choice(cards,deleted_cards))
    # money double







response = input("Do you want to play the game(y/n): ")
if response =="y":
    run=True
    number_of_player = input("How much players:  ")
else:
    run = False
while run:

    #gives cards to the dealer
    cards_dealer = []
    cards_dealer.append(random_card_choice(cards,deleted_cards))
    print("Dealer receive a card, you don't know the value")
    cards_dealer.append(random_card_choice(cards,deleted_cards))
    print("Dealer receive another card:", cards_dealer[1])



    #ask for the move
    for number in number_of_player:
        move = int(input("Wich move do you wanna do ? Hint (1), double (2), stand(3) "))
        if move==1:
            run_hint = True
            while run_hint:
                hint(cards_dealer, number, cards, deleted_cards)
                still_hint = int(input("Hint again(1) or pass(2) ? " ))
                if still_hint == 1 :
                    run_hint = True
                else:
                    run_hint = False
        elif move==2:
            double(cards_dealer,number,cards,deleted_cards)
            #give cards + score with code class
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
