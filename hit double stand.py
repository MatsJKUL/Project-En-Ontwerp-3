import pygame
import sys

pygame.init()

# Paramètres de la fenêtre
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini-jeu de cartes")

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Police de texte
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
player_action = None

# Variable pour contrôler si les boutons sont affichés
buttons_visible = True

# Variable pour contrôler la boucle principale
run = True

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and buttons_visible:
            # Vérification du clic sur l'un des boutons
            if hit_rect.collidepoint(event.pos):
                player_action = "hit"
            elif double_rect.collidepoint(event.pos):
                player_action = "double"
            elif stand_rect.collidepoint(event.pos):
                player_action = "stand"
            buttons_visible = False

    screen.fill(BLACK)

    # Affichage des boutons seulement si ils sont visibles
    if buttons_visible:
        screen.blit(button_hit, hit_rect.topleft)
        screen.blit(button_double, double_rect.topleft)
        screen.blit(button_stand, stand_rect.topleft)

    # Votre code principal ici

    pygame.display.flip()

pygame.quit()
sys.exit()
