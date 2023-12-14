
    def game_ask_for_bet(self):
        bet_render = pygame.font.Font(None, 36).render(f"PLACE YOUR BET {self.name}", True, (50, 50, 50))
        bet_render_rect = bet_render.get_rect()

        bet_render_rect.center = (
            int(self.screen_width/2), int(self.screen_height/2))

        pygame.draw.rect(
            self.screen, self.background, bet_render_rect)
        self.screen.blit(bet_render, bet_render_rect)

        pygame.display.update()
        self.clock.tick(30)


    def game_unblit_ask_for_bet(self):
        bet_render = pygame.font.Font(None, 36).render(f"PLACE YOUR BET {self.name}", True, (1, 150, 32))
        bet_render_rect = bet_render.get_rect()

        bet_render_rect.center = (
            int(self.screen_width/2), int(self.screen_height/2))

        pygame.draw.rect(
            self.screen, self.background, bet_render_rect)
        self.screen.blit(bet_render, bet_render_rect)

        pygame.display.update()
        self.clock.tick(30)
