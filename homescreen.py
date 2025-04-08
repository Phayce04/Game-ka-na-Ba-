import pygame
import os, sys
from sparkle import SparkleParticle 
from utils import board_matrix, q, MAX_TIME_LIMIT, WIDTH, HEIGHT, white, grey, black, blue, red, green, yellow, clock
import math 
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

    def draw_stage_light(self, frame_count):
        spotlight = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        # Fixed spotlight origin at top center
        top_center = (WIDTH // 2, 0)

        # Beam parameters
        beam_height = HEIGHT // 1.5
        base_half_width = 200  # Half of beam's base width
        sway_amplitude = 100
        sway_speed = 0.02

        # Calculate sway offset for beam rotation at the bottom
        sway = math.sin(frame_count * sway_speed) * sway_amplitude

        # Bottom corners pivoting around the fixed top
        bottom_left = (top_center[0] - base_half_width + sway, beam_height)
        bottom_right = (top_center[0] + base_half_width + sway, beam_height)

        # Draw the main light triangle (white with soft alpha)
        base_color = (255, 255, 255, 90)
        pygame.draw.polygon(spotlight, base_color, [top_center, bottom_left, bottom_right])

        # Optional soft layers for glow
        for i in range(5):
            fade = 90 - i * 12
            offset = i * 8
            points = [
                (top_center[0], top_center[1] + offset),
                (bottom_left[0] + offset, bottom_left[1]),
                (bottom_right[0] - offset, bottom_right[1])
            ]
            pygame.draw.polygon(spotlight, (255, 255, 255, fade), points)

        self.screen.blit(spotlight, (0, 0))

    def show(self):
        running = True
        frame_count = 0

        while running:
            self.screen.blit(self.bg_image, (0, 0))
            self.draw_stage_light(frame_count)  # << here
    
    
            frame_count += 1
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