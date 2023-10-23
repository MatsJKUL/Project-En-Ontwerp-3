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
stand_rect.topleft = (button_start_x + 2 * (button_hit.get_width() + button_spacing), button_y)

buttons_visible = True
move = None
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
    #before if move==1