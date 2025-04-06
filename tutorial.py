import pygame
import os, sys

white = (255,255,255)
grey = (160,160,160)
black = (0,0,0)
blue = (0,0,255)
red = (255,0,0)
green = (0,255,0)
yellow = (255,255,0)
clock = pygame.time.Clock()

WIDTH, HEIGHT = 1200,800
class TutorialScreen:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.font = pygame.font.SysFont('Arial', 36)
        try:
            # Replace 'tutorial.jpg' with your actual image file
            self.tutorial_image = pygame.image.load('tutorial.jpg')
            self.tutorial_image = pygame.transform.scale(self.tutorial_image, (WIDTH, HEIGHT))
        except:
            # Fallback if image doesn't load
            self.tutorial_image = None
            print("Could not load tutorial image")
        
        self.continue_text = self.font.render("Click anywhere to continue", True, white)
        self.continue_rect = self.continue_text.get_rect(center=(WIDTH//2, HEIGHT-50))
        
    def show(self):
        running = True
        while running:
            self.screen.fill(black)
            
            if self.tutorial_image:
                self.screen.blit(self.tutorial_image, (0, 0))
            else:
                # Fallback content if image didn't load
                title = self.font.render("Tutorial", True, white)
                self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
                
                instructions = [
                    "1. Select a team by clicking on their name",
                    "2. Click on a question value to see the question",
                    "3. Click again to see the answer",
                    "4. Click the green button if the team answered correctly",
                    "5. Click the red button if the answer was wrong",
                    "6. The team with the highest score wins!"
                ]
                
                for i, line in enumerate(instructions):
                    text = self.font.render(line, True, white)
                    self.screen.blit(text, (100, 150 + i*50))
            
            # Blinking "continue" text
            if pygame.time.get_ticks() % 1000 < 500:
                self.screen.blit(self.continue_text, self.continue_rect)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    running = False
            
            clock.tick(30)