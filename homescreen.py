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

        # Beam settings
        beam_length = HEIGHT * 0.95
        beam_width = 400
        sway_amplitude = 60
        sway_speed = 0.05

        # Define spotlights: farther apart, center moved upward
        lights = [
            {
                "top": (WIDTH // 2, -100),               # Top-center (off screen)
                "base_x": WIDTH // 2,
                "base_y": HEIGHT * 0.82,
                "offset": 0
            },
            {
                "top": (-80, 0),                         # Far top-left
                "base_x": WIDTH // 2 - 180,
                "base_y": HEIGHT * 0.88,
                "offset": math.pi / 2
            },
            {
                "top": (WIDTH + 80, 0),                  # Far top-right
                "base_x": WIDTH // 2 + 180,
                "base_y": HEIGHT * 0.88,
                "offset": math.pi
            }
        ]

        for light in lights:
            top_x, top_y = light["top"]
            base_x = light["base_x"]
            base_y = light["base_y"]

            # Sway the base left/right
            sway = math.sin(frame_count * sway_speed + light["offset"]) * sway_amplitude
            base_x += sway

            # Calculate beam corners
            left_x = base_x - beam_width // 2
            right_x = base_x + beam_width // 2
            bottom_y = base_y

            # Draw beam triangle (without any fading for now)
            main_color = (255, 255, 255, 90)
            pygame.draw.polygon(
                spotlight, main_color,
                [(top_x, top_y), (left_x, bottom_y), (right_x, bottom_y)]
            )

            # Apply fading at the bottom end (fading out towards the end, opposite the pivot)
            for i in range(5):
                alpha = 90 - i * 15  # Fade out from the pivot towards the base
                offset = i * 8

                # Fade the end of the beam (opposite the pivot)
                pygame.draw.polygon(
                    spotlight,
                    (255, 255, 255, max(0, alpha)),
                    [
                        (top_x, top_y + offset),  # Keep the pivot bright
                        (left_x + offset, bottom_y),  # Fade towards the bottom-left
                        (right_x - offset, bottom_y)  # Fade towards the bottom-right
                    ]
                )

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