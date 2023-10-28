import pygame
import os
import sys
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


# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1200, 800
CARD_WIDTH, CARD_HEIGHT = 50, 75
background = (1, 150, 32)

card_images = {}
card_path = 'cards/'  # Create a folder 'cards' and put card images inside
for suit in ['h', 'd', 'c', 's']:
    for rank in range(1, 14):
        card_name = f'{suit}{rank}.png'
        card_images[(suit, rank)] = pygame.image.load(
            os.path.join(card_path, card_name))
back = 'back'
card_images[(back, back)] = pygame.image.load(
    os.path.join(card_path, f'{back}.png'))

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blackjack Cards")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Police de texte
font = pygame.font.Font(None, 36)

# Création du bouton Play
# Variable pour le démarrage du code principal
running = False

# Variable pour contrôler la boucle principale
game_start = True

# Police de texte

# Création du bouton Play
play_button = font.render("Play", True, WHITE)
button_hit = font.render("Hit", True, WHITE)
button_double = font.render("Double", True, WHITE)
button_stand = font.render("Stand", True, WHITE)
split = font.render("Split", True, WHITE)
button_again = font.render("Play again", True, WHITE)
button_stop = font.render("Stop", True, WHITE)
play_rect = play_button.get_rect()
hit_rect = button_hit.get_rect()
double_rect = button_double.get_rect()
stand_rect = button_stand.get_rect()
split_rect = split.get_rect()
again_rect = button_again.get_rect()
stop_rect = button_stop.get_rect()
play_rect.center = (WIDTH // 2, HEIGHT // 2)
hit_rect.center = (50, 30)
double_rect.center = (210, 30)
stand_rect.center = (115, 30)
split_rect.center = (260, 30)
again_rect.center = (WIDTH // 2 - 100, HEIGHT // 2)
stop_rect.center = (WIDTH // 2 + 100, HEIGHT // 2)

# Variable pour le démarrage du code principal
game_started = False

# Variable pour le nombre de joueurs
number_of_player = 1

# Variable pour contrôler la boucle principale
run = True

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and not running:
            # Si le bouton Play est cliqué, démarrez le code principal
            if play_rect.collidepoint(event.pos):
                running = True
        if event.type == pygame.KEYDOWN and not running:
            # Incrémente le nombre de joueurs de 1 à 7 avec les touches numériques
            if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7]:
                number_of_player = int(event.unicode)
    screen.fill(BLACK)

    # Affichage du bouton Play
    if not running:
        screen.blit(play_button, play_rect)
        # Affichage du nombre de joueurs
        text = font.render("How many players : " +
                           str(number_of_player), True, WHITE)
        text_rect = text.get_rect()
        text_rect.center = (WIDTH // 2, HEIGHT // 2 + 50)
        screen.blit(text, text_rect)
        pygame.display.update()

    # Code principal (à exécuter après avoir cliqué sur "Play")
    if running:
        # Votre code principal ici
        run = False
        pygame.display.flip()


clock = pygame.time.Clock()
buttons_visible = False
while running:
    screen.fill(background)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Clear the screen
    pygame.display.update()
    clock.tick(30)
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
        # money double

     # int(input("How much players (max 7):  "))
    # gives cards to the players
    Player1 = Players()
    Player2 = Players()
    Player3 = Players()
    Player4 = Players()
    Player5 = Players()
    Player6 = Players()
    Player7 = Players()
    max_players = [Player1, Player2, Player3,
                   Player4, Player5, Player6, Player7]
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
    for number in range(len(players)):
        screen.blit(card_images[players[number].status()[0][0]], ((
            number+1) * WIDTH//(len(players)+1) - 60, 500))
        pygame.display.update()
        clock.tick(30)
        pygame.time.delay(500)
    # gives cards to the dealer
    dealer = Players()
    dealer.get_card(random_card_choice(cards, deleted_cards))
    print(dealer.status())
    screen.blit(card_images[dealer.status()[0][0]], (550, 30))
    points = font.render(str(dealer.status()[1]), True, WHITE)
    points_rect = points.get_rect()
    points_rect.center = (600, 180)
    screen.blit(points, points_rect)
    pygame.display.update()
    clock.tick(30)
    for number in range(len(players)):
        points = font.render(str(players[number].status()[1]), True, WHITE)
        points_rect = points.get_rect()
        points_rect.center = ((number + 1) * WIDTH // (len(players) + 1), 650)
        screen.blit(card_images[players[number].status()[0][1]], ((
            number+1) * WIDTH//(len(players)+1) + (len(players[number].status()[0])-1)*30 - 60, 500))
        pygame.draw.rect(screen, background, points_rect)
        screen.blit(points, points_rect)
        pygame.display.update()
        clock.tick(30)
        pygame.time.delay(500)
    dealer.get_card(random_card_choice(cards, deleted_cards))
    print("Dealer receive another card:", dealer.status()[0][1])
    screen.blit(card_images[(back, back)], (580, 30))
    pygame.display.update()
    clock.tick(30)
    pygame.time.delay(500)

    # ask for the move
    busted_player = []

    for number in range(len(players)):
        buttons_visible = True
        move = None
        turn = font.render("YOUR TURN", True, (50, 50, 50))
        turn_rect = turn.get_rect()
        turn_rect.center = ((number + 1) * WIDTH // (len(players) + 1), 450)
        screen.blit(turn, turn_rect)
        screen.blit(button_hit, hit_rect)
        screen.blit(button_double, double_rect)
        screen.blit(button_stand, stand_rect)
        pygame.display.update()
        clock.tick(30)
        pygame.draw.rect(screen, background, turn_rect)
        while buttons_visible:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and buttons_visible:
                    # Vérification du clic sur l'un des boutons
                    if hit_rect.collidepoint(event.pos):
                        move = 1
                    elif double_rect.collidepoint(event.pos):
                        move = 2
                    elif stand_rect.collidepoint(event.pos):
                        move = 3
                    pygame.draw.rect(screen, background, hit_rect)
                    pygame.draw.rect(screen, background, double_rect)
                    pygame.draw.rect(screen, background, stand_rect)
                    pygame.display.update()
                    clock.tick(30)
                    buttons_visible = False
        if move == 1:
            run_hit = True
            while run_hit:
                hit(players[number], cards, deleted_cards)
                points = font.render(
                    str(players[number].status()[1]), True, WHITE)
                points_rect = points.get_rect()
                points_rect.center = (
                    (number + 1) * WIDTH // (len(players) + 1), 650)
                player_status = players[number].status()
                screen.blit(card_images[players[number].status()[0][-1]], ((number+1) * WIDTH // (
                    len(players)+1) + (len(players[number].status()[0]) - 1) * 30 - 60, 500))
                pygame.draw.rect(screen, background, points_rect)
                screen.blit(points, points_rect)
                pygame.display.update()
                clock.tick(30)
                pygame.time.delay(500)
                print(
                    "You have",
                    player_status[0],
                    "as cards and:",
                    player_status[1],
                    "points.",
                )
                if player_status[1] > 21:
                    print("You are busted !")
                    busted = font.render("BUSTED", True, (255, 50, 50))
                    busted_rect = busted.get_rect()
                    busted_rect.center = (
                        (number + 1) * WIDTH // (len(players) + 1), 680)
                    screen.blit(busted, busted_rect)
                    pygame.display.update()
                    clock.tick(30)
                    busted_player.append(players[number])
                    run_hit = False
                else:
                    still_hit = None
                    buttons_visible = True
                    screen.blit(button_hit, hit_rect)
                    screen.blit(button_stand, stand_rect)
                    pygame.display.update()
                    clock.tick(30)
                    while buttons_visible:
                        for event in pygame.event.get():
                            if event.type == pygame.MOUSEBUTTONDOWN and buttons_visible:
                                # Vérification du clic sur l'un des boutons
                                if hit_rect.collidepoint(event.pos):
                                    still_hit = 1
                                elif stand_rect.collidepoint(event.pos):
                                    move = 3
                                pygame.draw.rect(screen, background, hit_rect)
                                pygame.draw.rect(
                                    screen, background, double_rect)
                                pygame.draw.rect(
                                    screen, background, stand_rect)
                                pygame.display.update()
                                clock.tick(30)
                                buttons_visible = False
                    if still_hit == 1:
                        run_hit = True
                    else:
                        run_hit = False
        elif move == 2:
            double(players[number], cards, deleted_cards)
            player_status = players[number].status()
            print(
                "You have",
                player_status[0],
                "as cards and:",
                player_status[1],
                "points.",
            )
            if player_status[1] > 21:
                busted = font.render("BUSTED", True, (255, 50, 50))
                busted_rect = busted.get_rect()
                busted_rect.center = (
                    (number + 1) * WIDTH // (len(players) + 1), 680)
                screen.blit(busted, busted_rect)
                pygame.display.update()
                clock.tick(30)
                print("You are busted !")
                busted_player.append(players[number])

            else:
                pass
        else:
            pass
    # delete busted players
    # Dealer game
    print("Dealer's turn !")
    dealer_takes_card = True
    dealer_busted = False
    screen.blit(card_images[dealer.status()[0][1]], (580, 30))
    points = font.render(str(dealer.status()[1]), True, WHITE)
    points_rect = points.get_rect()
    points_rect.center = (600, 180)
    pygame.draw.rect(screen, background, points_rect)
    screen.blit(points, points_rect)
    pygame.display.update()
    clock.tick(30)
    while dealer_takes_card:
        dealer_score = dealer.status()[1]
        print(
            "Dealer's card are",
            dealer.status()[0],
            "with a score of :",
            dealer_score,
            "points.",
        )
        if dealer_score > 21:
            print("Dealer busted. All the players won !!")
            busted = font.render("BUSTED", True, (255, 50, 50))
            busted_rect = busted.get_rect()
            busted_rect.center = (600, 210)
            screen.blit(busted, busted_rect)
            pygame.display.update()
            clock.tick(30)
            dealer_busted = True
            dealer_takes_card = False
        elif dealer_score >= 17:
            dealer_takes_card = False
        else:
            print("Dealer takes a new card")
            dealer.get_card(random_card_choice(cards, deleted_cards))
            screen.blit(card_images[dealer.status()[0][-1]],
                        (550 + (len(dealer.status()[0]) - 1) * 30, 30))
            points = font.render(str(dealer.status()[1]), True, WHITE)
            points_rect = points.get_rect()
            points_rect.center = (600, 180)
            pygame.draw.rect(screen, background, points_rect)
            screen.blit(points, points_rect)
            pygame.display.update()
            clock.tick(30)
    # Score players
        if dealer_busted == False:
            for number in range(0, len(players)):
                if players[number] in busted_player:
                    pass
                elif players[number].status()[1] > dealer_score:
                    you_win = font.render("YOU WON", True, WHITE)
                    you_win_rect = you_win.get_rect()
                    you_win_rect.center = (
                        (number + 1) * WIDTH // (len(players) + 1), 680)
                    screen.blit(you_win, you_win_rect)
                    pygame.display.update()
                    clock.tick(30)
                    print(
                        "Player " + str(number + 1),
                        "won with a score of",
                        players[number].status()[1],
                        "points.",
                    )
                elif players[number].status()[1] == dealer_score:
                    push = font.render("PUSH", True, WHITE)
                    push_rect = push.get_rect()
                    push_rect.center = (
                        (number + 1) * WIDTH // (len(players) + 1), 680)
                    screen.blit(push, push_rect)
                    pygame.display.update()
                    clock.tick(30)
                    print("Push. Player " + str(number + 1),
                          "has same score as the dealer")
                else:
                    you_lose = font.render("YOU LOST", True, WHITE)
                    you_lose_rect = you_lose.get_rect()
                    you_lose_rect.center = (
                        (number + 1) * WIDTH // (len(players) + 1), 680)
                    screen.blit(you_lose, you_lose_rect)
                    pygame.display.update()
                    clock.tick(30)
                    print(
                        "Player " + str(number + 1),
                        "lose with a score of",
                        players[number].status()[1],
                        "points.",
                    )

    # end of the game
    # Réinsérer les cartes retirées dans le set de base
    play_again = True
    cards.update((deleted_cards))
    screen.blit(button_again, again_rect)
    screen.blit(button_stop, stop_rect)
    pygame.display.update()
    clock.tick(30)
    while play_again:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and play_again:
                if again_rect.collidepoint(event.pos):
                    running = True
                elif stop_rect.collidepoint(event.pos):
                    print('stop')
                    running = False
                    pygame.quit()
                    sys.exit()
                pygame.draw.rect(screen, background, again_rect)
                pygame.draw.rect(screen, background, stop_rect)
                pygame.display.update()
                clock.tick(30)
                play_again = False