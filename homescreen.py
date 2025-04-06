import pygame
import os, sys
from sparkle import SparkleParticle 
from utils import board_matrix, q, MAX_TIME_LIMIT, WIDTH, HEIGHT, white, grey, black, blue, red, green, yellow, clock

class HomeScreen:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.bg_image = pygame.image.load("Larawan/trial.png")
        self.bg_image = pygame.transform.scale(self.bg_image, (WIDTH, HEIGHT))
        self.sparkles = [SparkleParticle() for _ in range(30)]  # More sparkles
        self.font = pygame.font.Font("Fonts/Fredoka-Regular.ttf", 40)
        self.text_alpha = 0
        self.text_alpha_change = 3  # Controls twinkle speed

    def draw_twinkle_text(self):
        # Update alpha value for twinkling
        self.text_alpha += self.text_alpha_change
        if self.text_alpha >= 255 or self.text_alpha <= 50:
            self.text_alpha_change *= -1
            self.text_alpha = max(50, min(255, self.text_alpha))

        # Render text with alpha
        text_surface = self.font.render("Click to Play", True, (255, 255, 255))
        text_surface.set_alpha(self.text_alpha)

        # Blit to screen at bottom center
        x = WIDTH // 2 - text_surface.get_width() // 2
        y = HEIGHT - 80
        self.screen.blit(text_surface, (x, y))

    def show(self):
        running = True
        while running:
            self.screen.blit(self.bg_image, (0, 0))

            for sparkle in self.sparkles:
                sparkle.update()
                sparkle.draw(self.screen)

            self.draw_twinkle_text()

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    return  # Start the game

# Usage