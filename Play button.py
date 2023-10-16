import pygame
import sys

pygame.init()

# Paramètres de la fenêtre
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Nombre de Joueurs")

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (1, 150, 32)

# Police de texte
font = pygame.font.Font(None, 36)

# Création du bouton Play
play_button = font.render("Play", True, WHITE)
play_rect = play_button.get_rect()
play_rect.center = (WIDTH // 2, HEIGHT // 2)

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
        if event.type == pygame.MOUSEBUTTONDOWN and not game_started:
            # Si le bouton Play est cliqué, démarrez le code principal
            if play_rect.collidepoint(event.pos):
                game_started = True
        if event.type == pygame.KEYDOWN and not game_started:
            # Incrémente le nombre de joueurs de 1 à 7 avec les touches numériques
            if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7]:
                number_of_player = int(event.unicode)

    screen.fill(BLACK)

    # Affichage du bouton Play
    if not game_started:
        pygame.draw.rect(screen, (50, 50, 50), play_rect)
        screen.blit(play_button, play_rect)
        # Affichage du nombre de joueurs
        text = font.render("How many players : " + str(number_of_player), True, WHITE)
        text_rect = text.get_rect()
        text_rect.center = (WIDTH // 2, HEIGHT // 2 + 50)
        screen.blit(text, text_rect)
        pygame.display.update()

    # Code principal (à exécuter après avoir cliqué sur "Play")
    if game_started:
        run = False
        # Votre code principal ici
font = pygame.font.Font(None, 36)

# Boutons
button_hit = font.render("Hit", True, WHITE)
button_double = font.render("Double", True, WHITE)
button_stand = font.render("Stand", True, WHITE)

# Zones des boutons
hit_rect = button_hit.get_rect()
double_rect = button_double.get_rect()
stand_rect = button_stand.get_rect()

# Position des boutons
button_spacing = 30
button_start_x = WIDTH // 2 - (button_hit.get_width() + button_spacing) * 1.5
button_y = HEIGHT // 2

hit_rect.topleft = (button_start_x, button_y)
double_rect.topleft = (button_start_x + button_hit.get_width() + button_spacing, button_y)
stand_rect.topleft = (button_start_x + 2 * (button_hit.get_width() + button_spacing), button_y)

# Variable pour l'action du joueur
move = None
screen.fill(GREEN)
pygame.display.update()
buttons_visible = True
while True:
    # after move input
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN and buttons_visible:
            # Vérification du clic sur l'un des boutons
            if hit_rect.collidepoint(event.pos):
                move = 1
            elif double_rect.collidepoint(event.pos):
                move = 2
            elif stand_rect.collidepoint(event.pos):
                move = 3
            buttons_visible = False
    screen.fill(GREEN)
    if buttons_visible:
        screen.blit(button_hit, hit_rect.topleft)
        screen.blit(button_double, double_rect.topleft)
        screen.blit(button_stand, stand_rect.topleft)
    pygame.display.flip()
    #before if move==1
pygame.quit()
sys.exit()
