import pygame
import random
import math
from utils import board_matrix, q, MAX_TIME_LIMIT, WIDTH, HEIGHT, white, grey, black, blue, red, green, yellow, clock
class SparkleParticle:
    def __init__(self, x=None, y=None):
        self.manual_position = (x, y) if x is not None and y is not None else None
        self.reset()

    def reset(self):
        self.size = random.randint(4, 8)
        self.alpha = random.randint(100, 255)
        self.alpha_change = random.choice([-4, -3, 3, 4])
        self.rotation = random.randint(0, 360)

        if self.manual_position:
            self.x, self.y = self.manual_position
        else:
            # Wider spread for ambient sparkles (outside center zone)
            margin = 100
            while True:
                self.x = random.randint(-margin, WIDTH + margin)
                self.y = random.randint(-margin, HEIGHT + margin)
                center_rect = pygame.Rect(WIDTH // 4, HEIGHT // 4, WIDTH // 2, HEIGHT // 2)
                if not center_rect.collidepoint(self.x, self.y):
                    break

    def update(self):
        self.alpha += self.alpha_change
        if self.alpha <= 80 or self.alpha >= 255:
            self.alpha_change *= -1
            self.alpha = max(80, min(255, self.alpha))
        
        self.rotation = (self.rotation + 0.5) % 360

    def draw(self, surface):
        total_size = self.size * 4
        star_surface = pygame.Surface((total_size * 2, total_size * 2), pygame.SRCALPHA)

        # Choose color based on manual/random
        if self.manual_position:
            color = (255, 215, 0, self.alpha)  # Gold
            glow_color = (255, 215, 0, int(self.alpha * 0.3))
            center_dot_color = (255, 255, 200, 255)  # Very bright center
            scale_multiplier = 1.5  # Slightly bigger for gold sparkles
        else:
            color = (255, 255, 255, self.alpha)  # White
            glow_color = (255, 255, 255, int(self.alpha * 0.3))
            center_dot_color = None
            scale_multiplier = 1.0

        # Glow behind star
        glow_radius = self.size * 1.5 * scale_multiplier
        pygame.draw.circle(star_surface, glow_color, (total_size, total_size), glow_radius)

        # Star points
        main_radius = self.size * 2.5 * scale_multiplier
        secondary_radius = self.size * 0.8 * scale_multiplier
        small_radius = self.size * 0.3 * scale_multiplier

        points = []
        for i in range(16):
            angle = math.pi * 2 * i / 16 - math.pi / 2
            if i % 4 == 0:
                radius = main_radius
            elif i % 2 == 0:
                radius = secondary_radius
            else:
                radius = small_radius

            x = total_size + radius * math.cos(angle + math.radians(self.rotation))
            y = total_size + radius * math.sin(angle + math.radians(self.rotation))
            points.append((x, y))

        # Star shape
        pygame.draw.polygon(star_surface, color, points)

        # Bright center dot for manual sparkles
        if center_dot_color:
            pygame.draw.circle(star_surface, center_dot_color, (total_size, total_size), int(self.size * 0.6))

        # Blit to screen
        surface.blit(star_surface, (self.x - total_size, self.y - total_size))

