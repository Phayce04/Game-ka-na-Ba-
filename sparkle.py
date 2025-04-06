import pygame
import random
import math
WIDTH, HEIGHT = 1200,800

class SparkleParticle:
    def __init__(self):
        self.reset()

    def reset(self):
        center_rect = pygame.Rect(WIDTH // 4, HEIGHT // 4, WIDTH // 2, HEIGHT // 2)

        while True:
            self.x = random.randint(0, WIDTH)
            self.y = random.randint(0, HEIGHT)
            if not center_rect.collidepoint(self.x, self.y):
                break

        self.size = random.randint(4, 8)  # Base size for the star
        self.alpha = random.randint(100, 255)
        self.alpha_change = random.choice([-4, -3, 3, 4])  # Twinkle speed
        self.rotation = random.randint(0, 360)  # Random initial rotation

    def update(self):
        self.alpha += self.alpha_change
        if self.alpha <= 80 or self.alpha >= 255:
            self.alpha_change *= -1
            self.alpha = max(80, min(255, self.alpha))
        
        # Slight rotation for more dynamic twinkling
        self.rotation = (self.rotation + 0.5) % 360

    def draw(self, surface):
        # Create a surface for the star with extra space for glow
        total_size = self.size * 4
        star_surface = pygame.Surface((total_size*2, total_size*2), pygame.SRCALPHA)
        
        # Draw faint glow first (behind the star)
        glow_radius = self.size * 1.5
        glow_alpha = int(self.alpha * 0.3)  # Glow is fainter than the star
        pygame.draw.circle(star_surface, (255, 255, 255, glow_alpha), 
                          (total_size, total_size), glow_radius)
        
        # Points for an 8-pointed star with longer main points
        main_radius = self.size * 2.5  # Length of the main points (longer)
        secondary_radius = self.size * 0.8  # Length of the secondary points
        small_radius = self.size * 0.3  # Very small center
        
        points = []
        for i in range(16):  # More points for smoother star
            angle = math.pi * 2 * i / 16 - math.pi/2  # Offset by -90 degrees
            if i % 4 == 0:
                # Main point (longest)
                radius = main_radius
            elif i % 2 == 0:
                # Secondary point
                radius = secondary_radius
            else:
                # Inner point (smallest)
                radius = small_radius
                
            x = total_size + radius * math.cos(angle + math.radians(self.rotation))
            y = total_size + radius * math.sin(angle + math.radians(self.rotation))
            points.append((x, y))
        
        # Draw the star with current alpha
        pygame.draw.polygon(star_surface, (255, 255, 255, self.alpha), points)
        
        # Blit the star surface onto the main surface
        surface.blit(star_surface, (self.x - total_size, self.y - total_size))