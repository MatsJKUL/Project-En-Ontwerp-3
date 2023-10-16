WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

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
        # Votre code principal ici
        pygame.display.flip()
