

class players:
    def __init__(self):
        self.cards = []
        self.points = 0
        self.amount_of_aces = 0
        self.add_points()


    def get_card(self,card):
        self.cards.append(card)
        self.add_points()

    def add_points(self):
        points = 0
        amount_of_aces = 0
        for card in self.cards:
            if type(card[1]) is int:
                points += card[1]

            elif card[1] == 'ace':
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
        print(self.cards)
        if self.points < 21:
            print(self.points)
        else:
            print('busted')

player1 = players()
player1.get_card(('klaveren',5))
player1.get_card(('klaveren','jack'))

player1.status()

import pygame
import sys
import os

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1200, 800
CARD_WIDTH, CARD_HEIGHT = 50, 75
background = (1, 150, 32)

# Load the card images
card_images = {}
card_path = 'cards/'  # Create a folder 'cards' and put card images inside
for suit in ['h', 'd', 'c', 's']:
    for rank in range(1, 14):
        card_name = f'{suit}{rank}.png'
        card_images[(suit, rank)] = pygame.image.load(os.path.join(card_path, card_name))
back = 'back'
card_images[(back, back)] = pygame.image.load(os.path.join(card_path,f'{back}.png'))

# Create a window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blackjack Cards")

# Main loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Clear the screen
    screen.fill(background)
    pygame.display.update()
    clock.tick(30)

    import random

    colors = ["h", "d", "c", "s"]
    Waarde = [1,2,3,4,5,6,7,8,9,10,11,12,13]

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



    #gives cards to the dealer
    cards_dealer = []
    cards_dealer.append(random_card_choice(cards,deleted_cards))
    print("Dealer receive a card, you don't know the value")
    screen.blit(card_images[(back,back)], (30, 10))

    cards_dealer.append(random_card_choice(cards,deleted_cards))

    print("Dealer receive another card:", cards_dealer[1])
    screen.blit(card_images[cards_dealer[1]], (10, 10))

    pygame.display.update()
    clock.tick(30)

pygame.quit()
sys.exit()