import os, sys
import pandas as pd
import pygame
import time
import subprocess
import os
import random
import math
from tutorial import TutorialScreen  
from homescreen import HomeScreen  
from tkinter import filedialog, Tk
from team import TeamSetupScreen
from loadquestion import load_questions
from utils import board_matrix, q, MAX_TIME_LIMIT, WIDTH, HEIGHT, white, grey, black, blue, red, green, yellow, clock
from sparkle import SparkleParticle
from pygame.locals import *




pygame.init()
answered_img = pygame.image.load("Larawan/parangpiattos.png")
answered_img = pygame.transform.scale(answered_img, (WIDTH // 6, HEIGHT/8))
pygame.mixer.init()
pygame.mixer.music.load('Tunog/bgm.wav')
pygame.mixer.music.set_volume(0)  
pygame.mixer.music.play(-1) 
gameDisplay = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption('Bilis Sagot')
clock = pygame.time.Clock()

class Player(object):
    def __init__(self):
        self.score = 0
    def set_score(self,score):
        self.score = score

if not pygame.font: print ('Warning, fonts disabled')
if not pygame.mixer: print ('Warning, sound disabled')
class GameOverScreen:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.font_large = pygame.font.Font('Fonts/bernoru-blackultraexpanded.otf', 72)  # Scores
        self.font_medium = pygame.font.Font('Fonts/bernoru-blackultraexpanded.otf', 56)
        self.font_small = pygame.font.Font('Fonts/ArchivoBlack-Regular.ttf', 56)  # Bigger + thinner
        self.font_thin_large = pygame.font.Font('Fonts/ArchivoBlack-Regular.ttf', 72)  # Winning team name
        self.font_tiny = pygame.font.Font('Fonts/bernoru-blackultraexpanded.otf', 20)

    def show(self, team_names, team_scores):
        num_teams = len(team_names)

        if num_teams == 2:
            self.bg_image = pygame.image.load('Larawan/gameover2.png').convert()
        elif num_teams == 3:
            self.bg_image = pygame.image.load('Larawan/gameover3.png').convert()
        elif num_teams == 4:
            self.bg_image = pygame.image.load('Larawan/gameover4.png').convert()

        self.bg_image = pygame.transform.scale(self.bg_image, (WIDTH, HEIGHT))

        pygame.mixer.music.stop()
        pygame.mixer.music.load('Tunog/bgm.wav')
        pygame.mixer.music.set_volume(1)
        pygame.mixer.music.play(-1)

        max_score = max(team_scores)
        winners = [i for i, score in enumerate(team_scores) if score == max_score]

        name_color = (238, 202, 62)  # eeca3e

        running = True
        while running:
            self.screen.blit(self.bg_image, (0, 0))
            pygame.draw.line(self.screen, (255, 0, 0), (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 2)
            # Winner display
            if len(winners) == 1:
                winner_name = team_names[winners[0]].upper()
                winner_text = self.font_thin_large.render(winner_name, True, white)
            else:
                winner_names = " & ".join([team_names[i].upper() for i in winners])
                winner_text = self.font_thin_large.render(winner_names, True, white)

            self.screen.blit(winner_text, (WIDTH // 2 - winner_text.get_width() // 2 + 50, 360))

            # Team names and scores
            gap_x = 130  # Default gap
            if num_teams == 4:  # Set gap to 30px when there are 4 teams
                gap_x = 40
            if num_teams == 3:  # Set gap to 30px when there are 4 teams
                gap_x = 120
            gap_y = 10
            y_offset = 530
            column_width = 285  # Fixed width for each team slot

            team_texts = []
            for name, score in zip(team_names, team_scores):
                name_surf = self.font_small.render(name.upper(), True, name_color)
                score_surf = self.font_medium.render(str(score), True, white)
                team_texts.append((name_surf, score_surf))

            total_width = (column_width + gap_x) * num_teams - gap_x
            start_x = WIDTH // 2 - total_width // 2
            x = start_x

            for i, (name_surf, score_surf) in enumerate(team_texts):
                # Center team name within each slot
                name_x = x + (column_width - name_surf.get_width()) // 2
                score_x = x + (column_width - score_surf.get_width()) // 2

                self.screen.blit(name_surf, (name_x, y_offset))
                self.screen.blit(score_surf, (score_x, y_offset + name_surf.get_height() + gap_y))

                # Debug rectangle for slot (for visual clarity)
                rect_x = x
                rect_y = y_offset - 10
                rect_height = name_surf.get_height() + score_surf.get_height() + gap_y + 20
                pygame.draw.rect(self.screen, (255, 0, 0), (rect_x, rect_y, column_width, rect_height), 2)

                # Move x to next slot
                x += column_width + gap_x

            # Blinking "click to continue"
            continue_text = self.font_tiny.render("click to continue", True, name_color)
            if pygame.time.get_ticks() % 1000 < 500:
                self.screen.blit(continue_text, (WIDTH // 2 - continue_text.get_width() // 2, HEIGHT - 120))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    running = False

            clock.tick(30)




class QuitScreen:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.font_medium = pygame.font.SysFont('Arial', 48)
        self.bg_image = pygame.image.load("Larawan/restart.png").convert()
        self.bg_image = pygame.transform.scale(self.bg_image, (WIDTH, HEIGHT))
        button_width = 300 * 2 - 100
        button_height = 100 * 2 - 30

        self.restart_button = Button(WIDTH // 2 - button_width // 2, HEIGHT // 2 - 50 - 120, button_width, button_height, "", (0, 255, 0, 0))
        self.quit_button = Button(WIDTH // 2 - button_width // 2, HEIGHT // 2 + 100 - 50, button_width, button_height, "", (255, 0, 0, 0))

        # Add gold sparkle to each button (manual position)
        restart_x = self.restart_button.rect.left + 10
        restart_y = self.restart_button.rect.top + 18
        quit_x = self.quit_button.rect.right - 5
        quit_y = self.quit_button.rect.top + 60

        self.restart_sparkle = SparkleParticle(restart_x, restart_y)
        self.quit_sparkle = SparkleParticle(quit_x, quit_y)

    def show(self):
        running = True
        while running:
            self.screen.blit(self.bg_image, (0, 0))

            self.restart_button.draw(self.screen)
            self.quit_button.draw(self.screen)

            # Update and draw sparkles
            self.restart_sparkle.update()
            self.restart_sparkle.draw(self.screen)

            self.quit_sparkle.update()
            self.quit_sparkle.draw(self.screen)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.restart_button.is_clicked(event.pos):
                        self.reset_game()
                        return "restart"
                    elif self.quit_button.is_clicked(event.pos):
                        pygame.quit()
                        sys.exit()

            clock.tick(30)



    def reset_game(self):
        """Resets all game variables to their initial state"""
        global p1, show_question_flag, start_flag, team_names, team_scores, already_selected
        global current_selected, team_selected, question_time, grid_drawn_flag
        global selected_team_index, show_timer_flag, Running_flag, game_state
        global main_game_music_playing

        # Reset game variables
        load_questions('qset4_Book.csv')  
        p1 = Player()
        show_question_flag = False
        start_flag = False
        team_names = []
        team_scores = []
        already_selected = []
        current_selected = [0, 0]
        team_selected = False
        question_time = False
        grid_drawn_flag = False
        selected_team_index = -1
        show_timer_flag = False
        Running_flag = True
        game_state = "HOME"
        show_status_message = False
        message_display_time = 0
        current_message = ""
        original_placeholder = ""
        main_game_music_playing = False

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color  # Expecting (R, G, B, A)
        self.font = pygame.font.SysFont('Arial', 36)
        
    def draw(self, surface):

        # Create a transparent surface with per-pixel alpha
        button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        button_surface.fill(self.color)  # Fill with RGBA color

        surface.blit(button_surface, self.rect.topleft)


        # Draw text if there is any
        if self.text:
            text_surface = self.font.render(self.text, True, black)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)

        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Pane(object):
    def __init__(self):
        self.font = pygame.font.Font("Fonts/bernoru-blackultraexpanded.otf", 15)
        self.score_font = pygame.font.Font("Fonts/bernoru-blackultraexpanded.otf", 17)
        self.placeholder_font = pygame.font.Font("Fonts/ArchivoBlack-Regular.ttf", 24)
        self.placeholder_rect = pygame.Rect(0, 6*(HEIGHT/8), WIDTH, HEIGHT/8)  # 7th row

        # Initialize with default placeholder text
        self.placeholder_text = "SELECT A TEAM"
        
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
        self.screen.fill(white)
        self.draw_grid_flag = True
        pygame.display.update()

    def draw_placeholder_area(self):
        """Draw only the placeholder area without redrawing everything"""
        pygame.draw.rect(self.screen, (20, 25, 80), self.placeholder_rect)
        pygame.draw.rect(self.screen, pygame.Color('#eeca3e'), self.placeholder_rect, 3)
        
        # Draw text
        text_surface = self.placeholder_font.render(self.placeholder_text, True, pygame.Color('#eeca3e'))
        text_shadow = self.placeholder_font.render(self.placeholder_text, True, (0, 0, 0))
        text_x = WIDTH // 2 - text_surface.get_width() // 2
        text_y = 6*(HEIGHT/8) + (HEIGHT/8)/2 - text_surface.get_height()//2
        
        self.screen.blit(text_shadow, (text_x + 2, text_y + 2))
        self.screen.blit(text_surface, (text_x, text_y))
        
        pygame.display.update(self.placeholder_rect)  

    def get_gradient_color(self, row, total_rows):
        top_color = pygame.Color(30, 60, 180)
        bottom_color = pygame.Color(138, 43, 226)
        ratio = row / total_rows
        return (
            int(top_color.r + (bottom_color.r - top_color.r) * ratio),
            int(top_color.g + (bottom_color.g - top_color.g) * ratio),
            int(top_color.b + (bottom_color.b - top_color.b) * ratio)
        )

    def draw_grid(self):
        if self.draw_grid_flag:
            self.screen.fill((8, 10, 60))  # Dark backdrop
            self.draw_grid_flag = False
            self.show_score()
            self.show_selected_box()

        cell_height = int(HEIGHT / 8)  # Cast to integer
        cell_width = WIDTH / 6

        # === Step 1: Determine max font size that fits ALL category names ===
        category_texts = [str(board_matrix[0][col]).upper() for col in range(6)]
        max_font_size = 26
        min_font_size = 12
        final_font_size = max_font_size

        for size in range(max_font_size, min_font_size - 1, -1):
            header_font = pygame.font.Font("Fonts/bernoru-blackultraexpanded.otf", size)
            if all(header_font.render(text, True, white).get_width() <= cell_width - 10 for text in category_texts):
                final_font_size = size
                break

        shared_header_font = pygame.font.Font("Fonts/bernoru-blackultraexpanded.otf", final_font_size)

        # === Step 2: Draw grid ===
        for row in range(7):  # Changed from 6 to 7 to include the new row
            for col in range(6):
                rect = pygame.Rect(col * cell_width, row * cell_height, cell_width, cell_height)

                if row == 0:
                    # Header cell: Gold background (#eeca3e)
                    pygame.draw.rect(self.screen, pygame.Color('#eeca3e'), rect)  # Gold header

                    # Glossy shine (softened for subtlety)
                    shine = pygame.Surface((cell_width, cell_height // 2), pygame.SRCALPHA)
                    pygame.draw.rect(shine, (255, 255, 255, 30), shine.get_rect())
                    self.screen.blit(shine, rect.topleft)

                    # Unique underline (gold glow)
                    underline_rect = pygame.Rect(
                        rect.left + 10,
                        rect.bottom - 8,
                        cell_width - 20,
                        3
                    )
                    pygame.draw.rect(self.screen, pygame.Color('#eeca3e'), underline_rect)  # Glowing gold underline

                    # Render header text (soft white for better readability)
                    header_text = category_texts[col]
                    header_text_surface = shared_header_font.render(header_text, True, (245, 245, 245))  # Soft white text
                    text_shadow = shared_header_font.render(header_text, True, (100, 100, 100))  # Soft gray shadow

                    text_x = col * cell_width + cell_width // 2 - header_text_surface.get_width() // 2
                    text_y = row * cell_height + cell_height // 2 - header_text_surface.get_height() // 2

                    self.screen.blit(text_shadow, (text_x + 2, text_y + 2))
                    self.screen.blit(header_text_surface, (text_x, text_y))

                elif row == 6:  # Placeholder row
                    # Draw background for the placeholder row
                    placeholder_rect = pygame.Rect(0, row * cell_height, WIDTH, cell_height)
                    pygame.draw.rect(self.screen, (20, 25, 80), placeholder_rect)
                    pygame.draw.rect(self.screen, pygame.Color('#eeca3e'), placeholder_rect, 3)
                    
                    # Use the current placeholder text
                    text_surface = self.placeholder_font.render(self.placeholder_text, True, pygame.Color('#eeca3e'))
                    text_shadow = self.placeholder_font.render(self.placeholder_text, True, (0, 0, 0))
                    
                    text_x = WIDTH // 2 - text_surface.get_width() // 2
                    text_y = row * cell_height + cell_height // 2 - text_surface.get_height() // 2
                    
                    self.screen.blit(text_shadow, (text_x + 2, text_y + 2))
                    self.screen.blit(text_surface, (text_x, text_y))
                else:
                    # Regular cell with gradient color (blue)
                    start_color = pygame.Color('#181a89')  # Darker blue
                    end_color = pygame.Color('#12116b')    # Lighter blue
                    gradient_rect = pygame.Rect(col * cell_width, row * cell_height, cell_width, cell_height)

                    # Gradient surface for each cell
                    gradient = pygame.Surface((cell_width, cell_height))
                    for y in range(cell_height):
                        ratio = y / cell_height
                        color = pygame.Color(
                            int(start_color.r + ratio * (end_color.r - start_color.r)),
                            int(start_color.g + ratio * (end_color.g - start_color.g)),
                            int(start_color.b + ratio * (end_color.b - start_color.b))
                        )
                        pygame.draw.line(gradient, color, (0, y), (cell_width, y))

                    self.screen.blit(gradient, (col * cell_width, row * cell_height))

                    # Regular gold borders
                    pygame.draw.rect(self.screen, pygame.Color('#eeca3e'), gradient_rect, 3)  # Gold border
                    pygame.draw.rect(self.screen, black, gradient_rect, 1)         # Black inner border

                    # Shine strip
                    shine_rect = pygame.Rect(col * cell_width + 5, row * cell_height + 5,
                                            cell_width - 10, 15)
                    shine = pygame.Surface((shine_rect.width, shine_rect.height), pygame.SRCALPHA)
                    pygame.draw.rect(shine, (255, 255, 255, 60), shine.get_rect())
                    self.screen.blit(shine, shine_rect)

                    # Add text to non-header cells (grid cells) and make sure the text is gold
                    if row > 0:
                        cell_font = pygame.font.Font("Fonts/bernoru-blackultraexpanded.otf", 18)
                        grid_text_surface = cell_font.render(str(board_matrix[row][col]), True, pygame.Color('#eeca3e'))  # Gold text
                        grid_text_rect = grid_text_surface.get_rect(center=(col * cell_width + cell_width // 2,
                                                                            row * cell_height + cell_height // 2))
                        self.screen.blit(grid_text_surface, grid_text_rect)

        pygame.display.update()

    # ... (rest of the Pane class methods remain the same)




    def clear_already_selected(self, col, row):
        cell_width = WIDTH // 6
        cell_height = HEIGHT / 8
        answered_img = pygame.image.load("Larawan/parangpiattos.png")
        answered_img = pygame.transform.scale(answered_img, (cell_width, cell_height))
        self.screen.blit(answered_img, (row * cell_width, col * cell_height))

    def show_score(self):
        score_area = pygame.Rect(0, HEIGHT / 8 * 7, WIDTH, HEIGHT / 8)
        pygame.draw.rect(self.screen, (30, 30, 80), score_area)
        pygame.draw.rect(self.screen, (255, 215, 0), score_area, 3)
        
        cell_width = WIDTH / 6
        for i, (name, score) in enumerate(zip(team_names, team_scores)):
            name_text = self.font.render(name, True, white)
            name_shadow = self.font.render(name, True, black)
            name_x = i * cell_width + cell_width // 2 - name_text.get_width() // 2

            score_text = self.score_font.render(f"₱{score:,}", True, (255, 215, 0))
            score_shadow = self.score_font.render(f"₱{score:,}", True, black)
            score_x = i * cell_width + cell_width // 2 - score_text.get_width() // 2

            self.screen.blit(name_shadow, (name_x + 2, (HEIGHT / 8 * 7) + 15 + 2))
            self.screen.blit(score_shadow, (score_x + 2, (HEIGHT / 8 * 7) + 45 + 2))
            self.screen.blit(name_text, (name_x, (HEIGHT / 8 * 7) + 15))
            self.screen.blit(score_text, (score_x, (HEIGHT / 8 * 7) + 45))

    def show_selected_box(self):
        if selected_team_index >= 0:
            cell_width = WIDTH / 6
            highlight_rect = pygame.Rect(
                selected_team_index * cell_width, 
                HEIGHT / 8 * 7, 
                cell_width, 
                HEIGHT / 8
            )
            
            highlight = pygame.Surface((cell_width, HEIGHT / 8), pygame.SRCALPHA)
            pygame.draw.rect(highlight, (255, 255, 255, 60), highlight.get_rect())
            self.screen.blit(highlight, highlight_rect)

            border_thickness = 3 + int(2 * math.sin(pygame.time.get_ticks() / 200))
            pygame.draw.rect(self.screen, (255, 215, 0), highlight_rect, border_thickness)

    def addText(self, pos, text):
        col, row = pos
        cell_width = WIDTH / 6
        cell_height = HEIGHT / 8

        if row == 0:
            return

        cell_font = pygame.font.Font("Fonts/bernoru-blackultraexpanded.otf", 18)
        shadow_offset = (2, 2)

        shadow_surface = cell_font.render(str(text), True, black)
        shadow_rect = shadow_surface.get_rect(center=(
            col * cell_width + cell_width // 2 + shadow_offset[0],
            row * cell_height + cell_height // 2 + shadow_offset[1]
        ))

        text_surface = cell_font.render(str(text), True, pygame.Color("#eeca3e"))

        text_rect = text_surface.get_rect(center=(
            col * cell_width + cell_width // 2,
            row * cell_height + cell_height // 2
        ))

        self.screen.blit(shadow_surface, shadow_rect)
        self.screen.blit(text_surface, text_rect)


class Question(object):
    def __init__(self):
        # Load custom font
        self.font = pygame.font.Font("Fonts/bernoru-blackultraexpanded.otf", 32)

        # Load question background image
        self.question_bg = pygame.image.load("Larawan/cards.png")
        self.question_bg = pygame.transform.scale(self.question_bg, (WIDTH, HEIGHT))

        # Load answer background image (different from question)
        self.answer_bg = pygame.image.load("Larawan/answers.png")  # Different image
        self.answer_bg = pygame.transform.scale(self.answer_bg, (WIDTH, HEIGHT))

        pygame.display.set_caption('Box Test')
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT + 200), 0, 32)
        pygame.display.update()

    def show(self, q):
        self.screen.blit(self.question_bg, (0, 0))

        # Set margins and calculate available width
        margin = 250
        max_width = WIDTH - 2 * margin
        line_height = self.font.get_linesize()
        text_y = HEIGHT // 2 - 50  # Starting Y position

        # Split text into words
        words = q.split(' ')
        lines = []
        current_line = []

        for word in words:
            # Test if adding this word would exceed the width
            test_line = ' '.join(current_line + [word])
            test_width = self.font.size(test_line)[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                # If current line isn't empty, finalize it
                if current_line:
                    lines.append(' '.join(current_line))
                # Start new line with current word
                current_line = [word]
        
        # Add the last line
        if current_line:
            lines.append(' '.join(current_line))

        # Render each line centered
        for line in lines:
            text_surface = self.font.render(line, True, (255, 255, 255))
            text_width = text_surface.get_width()
            text_x = margin + (max_width - text_width) // 2
            self.screen.blit(text_surface, (text_x, text_y))
            text_y += line_height  # Move down for next line

        pygame.display.update()
    def show_answer(self, text):
        self.screen.blit(self.answer_bg, (0, 0))
        sizeX, sizeY = self.font.size(text)
        max_width = WIDTH * 0.8
        text_x = (WIDTH * 0.1) + (max_width / 2) - (sizeX / 2)
        text_y = HEIGHT / 3 + 50

        self.screen.blit(self.font.render(str(text), True, (255, 255, 255)), (text_x, text_y))

        radius = 75
        y_pos = 520

        green_circle = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        red_circle = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        grey_circle = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)

        pygame.draw.circle(green_circle, (0, 255, 0, 0), (radius, radius), radius)
        pygame.draw.circle(red_circle, (255, 0, 0, 0), (radius, radius), radius)
        pygame.draw.circle(grey_circle, (128, 128, 128, 0), (radius, radius), radius)

        self.screen.blit(green_circle, (WIDTH / 6 + 150 - radius, y_pos))
        self.screen.blit(red_circle, (4 * (WIDTH / 6) + 120 - radius, y_pos))
        self.screen.blit(grey_circle, ((WIDTH / 2 - 20) - radius, y_pos))

        pygame.display.update()


class Timer(object):
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, 800), 0, 32)
        self.font = pygame.font.Font("Fonts/bernoru-blackultraexpanded.otf", 32)  # Custom font
        self.timer_x_pos = (WIDTH / 2) - (WIDTH / 12)
        self.timer_y_pos = 650  # Lower position
        self.counter = 0
        self.startTime = 0
        self.elapsed = 0
        self.time_expired = False
        self.buzzer_played = False
        self.timer_width = WIDTH / 6
        self.timer_height = 100
        
        self.timer_bg = pygame.Surface((self.timer_width, self.timer_height), pygame.SRCALPHA)
        self.timer_bg.fill((0, 0, 255, 0))

    def start(self):
        """Start or restart the timer"""
        self.startTime = time.perf_counter()
        self.time_expired = False
        self.buzzer_played = False

    def show(self):
        """Display the timer with a larger dark blue circle positioned lower on the screen"""
        self.elapsed = round(time.perf_counter() - self.startTime, 1)

        self.timer_y_pos = 667  
        circle_radius = 70
        circle_center = (
            int(self.timer_x_pos + self.timer_width / 2),
            int(self.timer_y_pos + self.timer_height / 2)
        )
        pygame.draw.circle(self.screen, (0, 0, 139), circle_center, circle_radius)
        timer_text = self.font.render(str(self.elapsed), True, (255, 255, 0))
        text_rect = timer_text.get_rect(center=circle_center)
        self.screen.blit(timer_text, text_rect)

        if self.elapsed >= MAX_TIME_LIMIT and not self.time_expired:
            self.time_expired = True
            if not self.buzzer_played:
                pygame.mixer.music.load('Tunog/buzzer2.wav')
                pygame.mixer.music.play()
                self.buzzer_played = True
            print("Time's up!")

# Button positions (unchanged)
exit_button_rect = pygame.Rect(WIDTH - 60, 10, 50, 30)
restart_button_rect = pygame.Rect(WIDTH // 2 - 60, HEIGHT // 2 + 60, 120, 40)

def draw_exit_button(screen):
    pygame.draw.rect(screen, (200, 0, 0), exit_button_rect)
    font = pygame.font.SysFont(None, 24)
    text = font.render("Exit", True, (255, 255, 255))
    screen.blit(text, (WIDTH - 50, 15))

def draw_restart_button(screen):
    pygame.draw.rect(screen, (0, 150, 0), restart_button_rect)
    font = pygame.font.SysFont(None, 32)
    text = font.render("Restart", True, (255, 255, 255))
    screen.blit(text, (WIDTH // 2 - 40, HEIGHT // 2 + 70))

class Cell(object):
    def __init__(self):
        self.X=0
        self.Y=0
        self.text=''


load_questions('qset4_Book.csv')  
p1 = Player()
show_question_flag=False
start_flag = False
team_names = []
team_scores = []
already_selected = []
current_selected=[0,0]
team_selected = False
question_time = False
pane1= Pane()
question_screen = Question()
timer = Timer()
grid_drawn_flag = False
selected_team_index=-1
show_timer_flag = False
Running_flag = True
game_state = "HOME"
main_game_music_playing = False 
show_status_message = False
message_display_time = 0
current_message = ""
original_placeholder = ""
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check for exit button click   
            if exit_button_rect.collidepoint(event.pos):
                pygame.quit()
                sys.exit()

            # Check for restart button click (only visible on certain screens)
            if game_state in ["GAME_OVER", "TEAM_SETUP"] and restart_button_rect.collidepoint(event.pos):
                GameOverScreen().reset_game()
                continue

    # State machine for different game screens
    if game_state == "HOME":
        home_screen = HomeScreen()
        home_screen.show()
        pygame.display.update()

        # Wait for click to proceed to tutorial
        game_state = "TUTORIAL"

    elif game_state == "TUTORIAL":
        tutorial = TutorialScreen()
        tutorial.show()
        pygame.display.update()

        # Wait for click to proceed to team setup
        game_state = "TEAM_SETUP"

    elif game_state == "TEAM_SETUP":
        team_setup = TeamSetupScreen()
        team_names, team_scores = team_setup.show()
        pygame.display.update()

        # Wait for click to proceed to main game
        game_state = "MAIN_GAME"

    elif game_state == "MAIN_GAME":
        click_count = 0
        if game_state == "MAIN_GAME" and not main_game_music_playing:
            pygame.mixer.music.stop()
            pygame.mixer.music.load('Tunog/trial.wav')
            pygame.mixer.music.set_volume(0) 
            pygame.mixer.music.play(-1)
            main_game_music_playing = True

        if len(already_selected) == 3:
            game_state = "GAME_OVER"
            continue  

        # Reset to team selection phase
        team_selected = False
        pane1.placeholder_text = "PUMILI NG KOPONAN"  # Directly update the text
        pane1.draw_placeholder_area()  # Only redraw the placeholder area

        while not question_time:
            r, c = 0, 0
            if not grid_drawn_flag:
                pane1.draw_grid()
                for i in range(6):  # 6 columns
                    for j in range(6):  # All rows (0-5)
                        pane1.addText((i, j), board_matrix[j][i])
                grid_drawn_flag = True

            for each_already_selected in already_selected:
                pane1.clear_already_selected(each_already_selected[0], each_already_selected[1])

            draw_exit_button(pygame.display.get_surface())
            if show_status_message:
                # Calculate current standings
                current_leader = max(range(len(team_scores)), key=lambda i: team_scores[i])
                leading_team = team_names[current_leader]
                team_name = team_names[message_data['team_index']]
                points = message_data['points']
                
                # Determine message
                if message_data['correct']:
                    if message_data['prev_leader'] != message_data['team_index'] and \
                    team_scores[message_data['team_index']] > team_scores[current_leader]:
                        message = f"NAKAKUHA SI {team_name} NG {points} PUNTOS, SYA NA ANG NANGUNGUNA!"
                    else:
                        lead = team_scores[current_leader] - sorted(team_scores)[-2]
                        message = f"NAKAKUHA SI {team_name} NG {points} PUNTOS, NANGUNGUNA PA RIN SI {leading_team} NG {lead}"
                else:
                    if message_data['prev_leader'] == message_data['team_index'] and \
                    current_leader != message_data['team_index']:
                        message = f"BUMABA NG {points} SI {team_name}, NANGUNGUNA NA SI {leading_team}"
                    elif team_scores[message_data['team_index']] == max(team_scores):
                        lead = team_scores[current_leader] - sorted(team_scores)[-2]
                        message = f"BUMABA NG {points} SI {team_name}, LAMANG PA RIN SILA NG {lead}"
                    else:
                        deficit = max(team_scores) - team_scores[message_data['team_index']]
                        message = f"BUMABA NG {points} SI {team_name}, KAILANGAN NA NYANG HUMABOL NG {deficit}"
                
                # Show message
                original_text = pane1.placeholder_text
                pane1.placeholder_text = message
                pane1.draw_placeholder_area()
                pygame.display.update()
                
                # Wait for 3 seconds then revert
                pygame.time.delay(3000)
                pane1.placeholder_text = original_text
                pane1.draw_placeholder_area()
                show_status_message = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if exit_button_rect.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()

                    if team_selected:
                        print('Board Time')
                        for col in range(6):  # Only 6 columns
                            if col * (WIDTH / 6) < event.pos[0] < (col + 1) * (WIDTH / 6):
                                c = col
                                for row in range(1, 6):  # Clickable rows: 1-5
                                    row_pixel = row * (HEIGHT / 8)
                                    if row_pixel < event.pos[1] < (row + 1) * (HEIGHT / 8):
                                        r = row 
                                        print('Clicked on:', r, c, 'SCORE:', board_matrix[r][c])
                                        show_question_flag = True
                                        if (r, c) not in already_selected:
                                            already_selected.append((r, c))
                                            current_selected = [r, c]
                                            question_time = True
                                        else:
                                            pane1.placeholder_text = "PUMILI NG IBA"
                                            pane1.draw_placeholder_area()

                    else:
                        print('First select a team')
                        if event.pos[1] > HEIGHT - (2 * (HEIGHT / 8)):
                            for col in range(6):
                                if col < len(team_names) and col * (WIDTH / 6) < event.pos[0] < (col + 1) * (WIDTH / 6):
                                    print('Selected Team:', col, 'Selected Team Name:', team_names[col], 'score', team_scores[col])
                                    selected_team_index = col
                                    pane1.show_selected_box()
                                    team_selected = True
                                    pane1.placeholder_text = "PUMILI NG TANONG"
                                    pane1.draw_placeholder_area()
                                    break

            pygame.display.update()
            clock.tick(60)

        while question_time:
            grid_drawn_flag = False
            if show_timer_flag and not timer.time_expired:
                timer.show()  # Show timer only if it hasn't expired yet

            if show_question_flag:
                print("Current Selected", current_selected)
                timer.start()  # Start the timer only when the question is displayed
                try:
                    question = q[current_selected[0], current_selected[1]]['question']
                    print("Question:", q[current_selected[0], current_selected[1]]['question'])
                except:
                    print('No Question Found For Position')
                question_screen.show(question)
                show_question_flag = False
                show_timer_flag = True

            draw_exit_button(pygame.display.get_surface())

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if exit_button_rect.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()

                    if event.pos[1] > 200:
                        click_count += 1
                        print(q[r, c]['answer'])
                        question_screen.show_answer(q[r, c]['answer'])
                        show_timer_flag = False
                        print("Selected Question", c, r, "Points:", board_matrix[c][r], 'Click Count:', click_count)
                        print("Question Time")
                    if click_count == 2:
                        # Store previous state for message logic
                        prev_scores = team_scores.copy()
                        prev_leader = max(range(len(team_scores)), key=lambda i: prev_scores[i])
                        
                        # Update scores
                        if event.pos[0] > (WIDTH / 6) and event.pos[0] < 2 * (WIDTH / 6):
                            team_scores[selected_team_index] += board_matrix[r][c]
                            correct = True
                        elif event.pos[0] > 4 * (WIDTH / 6) and event.pos[0] < 5 * (WIDTH / 6):
                            team_scores[selected_team_index] -= board_matrix[r][c]
                            correct = False
                        
                        # Reset game state
                        team_selected = False
                        question_time = False
                        pane1.draw_grid_flag = True
                        click_count = 0
                        
                        # Set flag to show message AFTER returning to grid
                        show_status_message = True
                        message_data = {
                            'correct': correct,
                            'points': board_matrix[r][c],
                            'team_index': selected_team_index,
                            'prev_scores': prev_scores,
                            'prev_leader': prev_leader
                        }

                   

            pygame.display.update()
            clock.tick(60)

    elif game_state == "GAME_OVER":
        game_over_screen = GameOverScreen()
        game_over_screen.show(team_names, team_scores)
        
        quit_screen = QuitScreen()
        action = quit_screen.show()
        
        if action == "restart":
            game_state = "HOME"  
        else:
            pass
