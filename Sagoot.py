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
from team import TeamSetupScreen, CSVSetupScreen
from loadquestion import load_questions
from utils import board_matrix, q, MAX_TIME_LIMIT, WIDTH, HEIGHT, white, grey, black, blue, red, green, yellow, clock
from sparkle import SparkleParticle
from pygame.locals import *
import cv2

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
        self.font_large = pygame.font.Font('Fonts/bernoru-blackultraexpanded.otf', 72)
        self.font_medium = pygame.font.Font('Fonts/bernoru-blackultraexpanded.otf', 56)
        self.font_small = pygame.font.Font('Fonts/ArchivoBlack-Regular.ttf', 56)
        self.font_thin_large = pygame.font.Font('Fonts/ArchivoBlack-Regular.ttf', 72)
        self.font_tiny = pygame.font.Font('Fonts/bernoru-blackultraexpanded.otf', 20)
        
        # Initialize sparkles list (will be populated in show() method)
        self.team_sparkles = []
        # Load team background image
        self.team_bg = pygame.image.load('Larawan/Bg5.png').convert()

    def show(self, team_names, team_scores):
        num_teams = len(team_names)
        self.bg_image = pygame.image.load('Larawan/gameover.png').convert()
        self.bg_image = pygame.transform.scale(self.bg_image, (WIDTH, HEIGHT))

        pygame.mixer.music.stop()
        pygame.mixer.music.load('Tunog/bgm.wav')
        pygame.mixer.music.set_volume(1)
        pygame.mixer.music.play(-1)

        max_score = max(team_scores)
        winners = [i for i, score in enumerate(team_scores) if score == max_score]
        name_color = (238, 202, 62)  # eeca3e
        gold_color = (212, 175, 55)  # Gold color for borders
        self.team_sparkles = []
        gap_x = 130
        if num_teams == 4:
            gap_x = 40
        if num_teams == 3:
            gap_x = 120
            
        y_offset = 530
        column_width = 285
        total_width = (column_width + gap_x) * num_teams - gap_x
        start_x = WIDTH // 2 - total_width // 2
        
        for i in range(num_teams):
            x = start_x + i * (column_width + gap_x)
            # Random position along the border (top, right, bottom, or left)
            border_side = random.randint(0, 3)
            if border_side == 0:  # Top border
                sparkle_x = x + random.randint(10, column_width - 10)
                sparkle_y = y_offset - 10
            elif border_side == 1:  # Right border
                sparkle_x = x + column_width
                sparkle_y = y_offset - 10 + random.randint(10, 140)
            elif border_side == 2:  # Bottom border
                sparkle_x = x + random.randint(10, column_width - 10)
                sparkle_y = y_offset + 140
            else:  # Left border
                sparkle_x = x
                sparkle_y = y_offset - 10 + random.randint(10, 140)
            
            self.team_sparkles.append(SparkleParticle(sparkle_x, sparkle_y))

        running = True
        while running:
            self.screen.blit(self.bg_image, (0, 0))
            # pygame.draw.line(self.screen, gold_color, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 4)

            # Winner display
            if len(winners) == 1:
                winner_name = team_names[winners[0]].upper()
                winner_text = self.font_thin_large.render(winner_name, True, white)
            else:
                winner_names = " & ".join([team_names[i].upper() for i in winners])
                winner_text = self.font_thin_large.render(winner_names, True, white)

            self.screen.blit(winner_text, (WIDTH // 2 - winner_text.get_width() // 2 + 50, 360))

            # Team names and scores with gold borders
            x = start_x
            for i, (name, score) in enumerate(zip(team_names, team_scores)):
                # Draw team background
                team_bg_scaled = pygame.transform.scale(self.team_bg, (column_width, 140))
                self.screen.blit(team_bg_scaled, (x, y_offset - 10))
                
                name_surf = self.font_small.render(name.upper(), True, name_color)
                score_surf = self.font_medium.render(str(score), True, white)

                name_x = x + (column_width - name_surf.get_width()) // 2
                score_x = x + (column_width - score_surf.get_width()) // 2

                self.screen.blit(name_surf, (name_x, y_offset))
                self.screen.blit(score_surf, (score_x, y_offset + name_surf.get_height() ))

                # Draw gold border
                rect_x = x
                rect_y = y_offset - 10
                rect_height = name_surf.get_height() + score_surf.get_height() + 30
                pygame.draw.rect(self.screen, gold_color, (rect_x, rect_y, column_width, rect_height), 8)

                # Update and draw sparkle for this team's border
                self.team_sparkles[i].update()
                self.team_sparkles[i].draw(self.screen)

                x += column_width + gap_x

            # Blinking "click to continue"
            continue_text = self.font_tiny.render("click to continue", True, name_color)
            if pygame.time.get_ticks() % 1000 < 500:
                self.screen.blit(continue_text, (WIDTH // 2 - continue_text.get_width() // 2, HEIGHT - 150))

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
        
        # Load both video backgrounds
        self.restart_video = cv2.VideoCapture("Larawan/restart.mp4")
        self.quit_video = cv2.VideoCapture("Larawan/quit.mp4")
        self.current_video = self.restart_video  # Start with restart video
        self.selected_option = "restart"  # Track current selection
        
        button_width = 300 * 2 - 100
        button_height = 100 * 2 - 30

        self.restart_button = Button(WIDTH // 2 - button_width // 2, HEIGHT // 2 - 50 - 120, button_width, button_height, "", (0, 255, 0, 0))
        self.quit_button = Button(WIDTH // 2 - button_width // 2, HEIGHT // 2 + 100 - 50, button_width, button_height, "", (255, 0, 0, 0))

        # Sparkles
        restart_x = self.restart_button.rect.left + 10
        restart_y = self.restart_button.rect.top + 18
        quit_x = self.quit_button.rect.right - 5
        quit_y = self.quit_button.rect.top + 60

        self.restart_sparkle = SparkleParticle(restart_x, restart_y)
        self.quit_sparkle = SparkleParticle(quit_x, quit_y)

    def get_video_frame(self):
        ret, frame = self.current_video.read()
        if not ret or frame is None:
            self.current_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.current_video.read()
            if not ret or frame is None:
                return pygame.Surface((WIDTH, HEIGHT))
        frame = cv2.resize(frame, (WIDTH, HEIGHT))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return pygame.surfarray.make_surface(frame.swapaxes(0, 1))

    def switch_video(self):
        """Toggle between restart and quit videos"""
        if self.selected_option == "restart":
            self.current_video = self.quit_video
            self.selected_option = "quit"
        else:
            self.current_video = self.restart_video
            self.selected_option = "restart"
        # Reset video position when switching
        self.current_video.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def show(self):
        running = True
        while running:
            # Draw current video frame
            video_frame = self.get_video_frame()
            self.screen.blit(video_frame, (0, 0))

            # Draw UI elements
            self.restart_button.draw(self.screen)
            self.quit_button.draw(self.screen)
            self.restart_sparkle.update()
            self.restart_sparkle.draw(self.screen)
            self.quit_sparkle.update()
            self.quit_sparkle.draw(self.screen)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_DOWN):
                        self.switch_video()
                
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
        self.restart_video.release()
        self.quit_video.release()

        # Reset game variables
        load_questions('Katanungan/default-na-tanong.csv')  
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
        message="Pumili ng Koponan"
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
        self.placeholder_text = "SELECT A TEAM"
        self.placeholder_rect = pygame.Rect(0, 6 * (HEIGHT / 8), WIDTH, HEIGHT / 8)
        self.message_bg = pygame.image.load("Larawan/BG2.png").convert()
        self.message_bg = pygame.transform.scale(self.message_bg, (WIDTH, int(HEIGHT / 8)))

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
        self.screen.fill(white)
        self.draw_grid_flag = True
        self.sparkles = []

        pygame.display.update()

    def draw_placeholder_area(self):
        self.screen.blit(self.message_bg, self.placeholder_rect)
        self.placeholder_bg_copy = self.screen.subsurface(self.placeholder_rect).copy()

        # Animate text scale (simplified)
        text_surface = self.placeholder_font.render(self.placeholder_text, True, pygame.Color('#eeca3e'))
        text_shadow = self.placeholder_font.render(self.placeholder_text, True, (0, 0, 0))

        x = WIDTH // 2 - text_surface.get_width() // 2
        y = self.placeholder_rect.centery - text_surface.get_height() // 2

        self.screen.blit(text_shadow, (x + 2, y + 2))
        self.screen.blit(text_surface, (x, y))

    def show_score_notification(self, message_data):
        duration = 3000
        start_time = pygame.time.get_ticks()

        original_text = self.placeholder_text
        self.placeholder_text = ""  # Temporarily clear it to not draw under notification

        # Determine message
        current_leader = max(range(len(team_scores)), key=lambda i: team_scores[i])
        leading_team = team_names[current_leader]
        team_name = team_names[message_data['team_index']]
        points = message_data['points']

        if message_data['correct']:
            if message_data['prev_leader'] != message_data['team_index'] and \
                    team_scores[message_data['team_index']] > team_scores[current_leader]:
                message = f"NAKAKUHA ANG {team_name} NG {points} PUNTOS, SILA NA ANG NANGUNGUNA!"
                color = pygame.Color('#ffd700')
            else:
                lead = team_scores[current_leader] - sorted(team_scores)[-2]
                message = f"NAKAKUHA ANG {team_name} NG {points} PUNTOS, NANGUNGUNA PA RIN ANG {leading_team} NG {lead}"
                color = pygame.Color('#FFD700')
        else:
            if message_data['prev_leader'] == message_data['team_index'] and \
                    current_leader != message_data['team_index']:
                message = f"BUMABA NG {points} ANG {team_name}, NANGUNGUNA NA ANG {leading_team}"
                color = pygame.Color('#ff0000')
            elif team_scores[message_data['team_index']] == max(team_scores):
                lead = team_scores[current_leader] - sorted(team_scores)[-2]
                message = f"BUMABA NG {points} ANG {team_name}, LAMANG PA RIN SILA NG {lead}"
                color = pygame.Color('#ffa500')
            else:
                deficit = max(team_scores) - team_scores[message_data['team_index']]
                message = f"BUMABA NG {points} ANG {team_name}, KAILANGAN NA NIYANG HUMABOL NG {deficit}"
                color = pygame.Color('#ff6347')

        # Draw static message once
        pygame.draw.rect(self.screen, color, self.placeholder_rect)
        font = pygame.font.Font("Fonts/ArchivoBlack-Regular.ttf", 32)
        text_surface = font.render(message, True, white)
        shadow_surface = font.render(message, True, black)
        x = WIDTH // 2 - text_surface.get_width() // 2
        y = self.placeholder_rect.centery - text_surface.get_height() // 2
        self.screen.blit(shadow_surface, (x + 2, y + 2))
        self.screen.blit(text_surface, (x, y))

        if selected_team_index >= 0:
            self.show_selected_box()

        pygame.display.update(self.placeholder_rect)

        # Simple time delay instead of animation loop
        while pygame.time.get_ticks() - start_time < duration:
            clock.tick(60)

        self.placeholder_text = original_text
        self.draw_placeholder_area()
        self.draw_grid()
        self.show_score()
        if selected_team_index >= 0:
            self.show_selected_box()
        pygame.display.update()


    def draw_confetti(self, progress):
        for _ in range(2):
            x = random.randint(self.placeholder_rect.left, self.placeholder_rect.right)
            y = random.randint(self.placeholder_rect.top - 30, self.placeholder_rect.top)
            color = random.choice([red, green, blue, yellow, white])
            size = random.randint(2, 6)
            speed = random.uniform(1, 3)
            self.confetti_particles.append({
                'x': x, 'y': y, 'color': color, 'size': size, 'speed': speed,
                'angle': random.uniform(0, 2 * math.pi)
            })

        for particle in self.confetti_particles:
            particle['y'] += particle['speed']
            particle['x'] += math.sin(particle['angle']) * 0.5
            particle['angle'] += 0.1

            if self.placeholder_rect.collidepoint(particle['x'], particle['y']):
                pygame.draw.rect(
                    self.screen,
                    particle['color'],
                    (particle['x'], particle['y'], particle['size'], particle['size'])
                )

            if particle['y'] > self.placeholder_rect.bottom:
                particle['y'] = self.placeholder_rect.top - random.randint(20, 100)
                particle['x'] = random.randint(self.placeholder_rect.left, self.placeholder_rect.right)

        if progress >= 1.0:
            self.confetti_particles = []




    def draw_grid(self):
        if self.draw_grid_flag:
            self.screen.fill((8, 10, 60))  # Dark backdrop
            self.draw_grid_flag = False
            self.show_score()
            self.show_selected_box()

        cell_height = int(HEIGHT / 8)
        cell_width = WIDTH / 6

        # Step 1: Adjust header font size to fit all category names
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

        # Step 2: Draw each cell
        for row in range(7):  # Including the placeholder/message row
            for col in range(6):
                rect = pygame.Rect(col * cell_width, row * cell_height, cell_width, cell_height)

                if row == 0:
                    # Header cell
                    pygame.draw.rect(self.screen, pygame.Color('#eeca3e'), rect)

                    # Shine
                    shine = pygame.Surface((cell_width, cell_height // 2), pygame.SRCALPHA)
                    pygame.draw.rect(shine, (255, 255, 255, 30), shine.get_rect())
                    self.screen.blit(shine, rect.topleft)

                    # Underline
                    underline_rect = pygame.Rect(rect.left + 10, rect.bottom - 8, cell_width - 20, 3)
                    pygame.draw.rect(self.screen, pygame.Color('#eeca3e'), underline_rect)

                    # Text and shadow
                    header_text = category_texts[col]
                    header_text_surface = shared_header_font.render(header_text, True, (245, 245, 245))
                    text_shadow = shared_header_font.render(header_text, True, (100, 100, 100))

                    text_x = col * cell_width + cell_width // 2 - header_text_surface.get_width() // 2
                    text_y = row * cell_height + cell_height // 2 - header_text_surface.get_height() // 2

                    self.screen.blit(text_shadow, (text_x + 2, text_y + 2))
                    self.screen.blit(header_text_surface, (text_x, text_y))

                elif row == 6:
                    # Placeholder/message row (spans the entire width)
                    placeholder_rect = pygame.Rect(0, row * cell_height, WIDTH, cell_height)
                    pygame.draw.rect(self.screen, (20, 25, 80), placeholder_rect)
                    pygame.draw.rect(self.screen, pygame.Color('#eeca3e'), placeholder_rect, 3)

                    text_surface = self.placeholder_font.render(self.placeholder_text, True, pygame.Color('#eeca3e'))
                    text_shadow = self.placeholder_font.render(self.placeholder_text, True, (0, 0, 0))

                    text_x = WIDTH // 2 - text_surface.get_width() // 2
                    text_y = row * cell_height + cell_height // 2 - text_surface.get_height() // 2

                    self.screen.blit(text_shadow, (text_x + 2, text_y + 2))
                    self.screen.blit(text_surface, (text_x, text_y))
                    break  # Only draw one message row, so exit inner loop

                else:
                    # Regular cell with gradient background
                    start_color = pygame.Color('#181a89')
                    end_color = pygame.Color('#12116b')
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

                    pygame.draw.rect(self.screen, pygame.Color('#eeca3e'), rect, 3)
                    pygame.draw.rect(self.screen, black, rect, 1)

                    # Shine strip
                    shine_rect = pygame.Rect(col * cell_width + 5, row * cell_height + 5, cell_width - 10, 15)
                    shine = pygame.Surface((shine_rect.width, shine_rect.height), pygame.SRCALPHA)
                    pygame.draw.rect(shine, (255, 255, 255, 60), shine.get_rect())
                    self.screen.blit(shine, shine_rect)

                    # Grid cell text (gold)
                    cell_font = pygame.font.Font("Fonts/bernoru-blackultraexpanded.otf", 18)
                    cell_value = str(board_matrix[row][col])
                    grid_text_surface = cell_font.render(cell_value, True, pygame.Color('#eeca3e'))
                    grid_text_rect = grid_text_surface.get_rect(center=(col * cell_width + cell_width // 2,
                                                                        row * cell_height + cell_height // 2))
                    self.screen.blit(grid_text_surface, grid_text_rect)

        pygame.display.update()




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

class SparkleParticles:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(2, 5)
        self.color = random.choice([
            (255, 255, 255),  # White
            (255, 255, 0),    # Yellow
            (255, 215, 0),    # Gold
            (255, 165, 0)     # Orange
        ])
        self.speed = random.uniform(0.5, 2)
        self.angle = random.uniform(0, 2 * math.pi)
        self.lifetime = random.randint(20, 60)
        self.max_lifetime = self.lifetime
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-5, 5)
    
    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.lifetime -= 1
        self.rotation += self.rotation_speed
        # Fade out as lifetime decreases
        self.current_alpha = int(255 * (self.lifetime / self.max_lifetime))
    
    def draw(self, surface):
        # Create a surface with per-pixel alpha
        particle_surface = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        
        # Draw a star shape
        points = []
        for i in range(5):
            angle = math.radians(self.rotation + i * 72)
            outer_x = math.cos(angle) * self.size
            outer_y = math.sin(angle) * self.size
            inner_angle = angle + math.radians(36)
            inner_x = math.cos(inner_angle) * (self.size / 2)
            inner_y = math.sin(inner_angle) * (self.size / 2)
            points.extend([(self.size + outer_x, self.size + outer_y), 
                          (self.size + inner_x, self.size + inner_y)])
        
        # Draw with fading alpha
        color_with_alpha = (*self.color[:3], self.current_alpha)
        pygame.draw.polygon(particle_surface, color_with_alpha, points)
        
        # Draw to main surface
        surface.blit(particle_surface, (self.x - self.size, self.y - self.size))
class Question(object):
    def __init__(self):
        # Load custom font
        self.font = pygame.font.Font("Fonts/bernoru-blackultraexpanded.otf", 32)

        # Load video backgrounds
        self.question_video = cv2.VideoCapture("Larawan/question.mp4")
        self.answer_video = cv2.VideoCapture("Larawan/answer.mp4")

        pygame.display.set_caption('Box Test')
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT + 200), 0, 32)

    def get_video_frame(self, video_capture):
        ret, frame = video_capture.read()
        if not ret or frame is None:
            video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop the video
            ret, frame = video_capture.read()
            if not ret or frame is None:
                return pygame.Surface((WIDTH, HEIGHT))  # Fallback

        frame = cv2.resize(frame, (WIDTH, HEIGHT))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return pygame.surfarray.make_surface(frame.swapaxes(0, 1))

    def show_question(self, question_text):
        # Get and draw video frame
        video_frame = self.get_video_frame(self.question_video)
        self.screen.blit(video_frame, (0, 0))

        # Only render text if provided and not empty
        if question_text and str(question_text).strip():
            margin = 250
            max_width = WIDTH - 2 * margin
            line_height = self.font.get_linesize()
            text_y = HEIGHT // 2 - 50

            words = question_text.split(' ')
            lines = []
            current_line = []

            for word in words:
                test_line = ' '.join(current_line + [word])
                test_width = self.font.size(test_line)[0]

                if test_width <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]

            if current_line:
                lines.append(' '.join(current_line))

            # Create a surface for the text
            text_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            for line in lines:
                line_surface = self.font.render(line, True, (255, 255, 255))
                text_width = line_surface.get_width()
                text_x = margin + (max_width - text_width) // 2
                text_surface.blit(line_surface, (text_x, text_y))
                text_y += line_height

            # Blit the text surface onto the screen
            self.screen.blit(text_surface, (0, 0))

        pygame.display.update()


    def show_answer(self, answer_text):
        """Show answer with video background and buttons"""
        video_frame = self.get_video_frame(self.answer_video)
        self.screen.blit(video_frame, (0, 0))
        sizeX, sizeY = self.font.size(answer_text)
        max_width = WIDTH * 0.8
        text_x = (WIDTH * 0.1) + (max_width / 2) - (sizeX / 2)
        text_y = HEIGHT / 3 + 50
        self.screen.blit(self.font.render(str(answer_text), True, (255, 255, 255)), (text_x, text_y))

        # Draw the buttons (circles)
        radius = 75
        y_pos = 520

        # Create button surfaces
        buttons = []
        colors = [(0, 255, 0), (255, 0, 0), (128, 128, 128)]  # Green, Red, Grey
        positions = [
            (WIDTH / 6 + 150 - radius, y_pos),  # Green
            (4 * (WIDTH / 6) + 120 - radius, y_pos),  # Red
            ((WIDTH / 2 - 20) - radius, y_pos)  # Grey
        ]

        for color, pos in zip(colors, positions):
            circle = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(circle, (*color, 0), (radius, radius), radius)
            self.screen.blit(circle, pos)
            buttons.append(pygame.Rect(pos[0], pos[1], radius*2, radius*2))

        pygame.display.update()
        return buttons  # Return list of button rectangles for collision detection
class Timer(object):
    def __init__(self):
        self.font = pygame.font.Font("Fonts/bernoru-blackultraexpanded.otf", 40)
        self.timer_x_pos = (WIDTH / 2) - (WIDTH / 12)
        self.timer_y_pos = 660
        self.startTime = 0
        self.elapsed = 0
        self.time_expired = False
        self.buzzer_played = False
        self.timer_width = WIDTH / 6
        self.timer_height = 100
        self.circle_radius = 70
        self.active = False  # New state variable

    def start(self):
        self.startTime = time.perf_counter()
        self.time_expired = False
        self.buzzer_played = False
        self.active = True  # Activate timer

    def stop(self):
        self.active = False  # Deactivate timer

    def update(self):
        if self.active and not self.time_expired:
            self.elapsed = round(time.perf_counter() - self.startTime, 1)
            if self.elapsed >= MAX_TIME_LIMIT:
                self.time_expired = True
                if not self.buzzer_played:
                    pygame.mixer.music.load('Tunog/buzzer2.wav')
                    pygame.mixer.music.play()
                    self.buzzer_played = True
                print("Time's up!")

    def draw(self, screen):
        if self.active:
            # Format time to show 1 decimal place
            time_text = f"{self.elapsed:.1f}" if self.elapsed < 10 else f"{int(self.elapsed)}"
            
            # Render the timer text with larger font
            timer_text = self.font.render(time_text, True, (255, 255, 255))  # Dark blue color
            
            # Center the text
            text_rect = timer_text.get_rect(
                center=(self.timer_x_pos + self.timer_width/2, 
                       self.timer_y_pos + self.timer_height/2)
            )
            
            # Draw the text
            screen.blit(timer_text, text_rect)
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


load_questions('Katanungan/default-na-tanong.csv')  
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
showing_answer = False
current_answer = ""
button_rects = None
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

    if game_state == "HOME":
        home_screen = HomeScreen()
        home_screen.show()
        pygame.display.update()
        
        # Home screen only has next button
        game_state = "TUTORIAL"

    elif game_state == "TUTORIAL":
        tutorial = TutorialScreen()
        result = tutorial.show()
        pygame.display.update()
        
        game_state = "CSV_SETUP"


    elif game_state == "CSV_SETUP":
        csv_screen = CSVSetupScreen()
        result = csv_screen.show()
        pygame.display.update()
        
        if result == "NEXT":
            game_state = "TEAM_SETUP"
        elif result == "PREVIOUS":
            game_state = "TUTORIAL"

    elif game_state == "TEAM_SETUP":
        team_setup = TeamSetupScreen()
        result, team_names, team_scores = team_setup.show()
        pygame.display.update()
        
        if result == "NEXT":
            game_state = "MAIN_GAME"
        elif result == "PREVIOUS":
            game_state = "CSV_SETUP"


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

            # draw_exit_button(pygame.display.get_surface())
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
                pane1.show_score_notification(message_data)
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
            
            if showing_answer:
                button_rects = question_screen.show_answer(current_answer)
                timer.stop()  # Stop timer when showing answer
            else:
                if show_question_flag:
                    print("Current Selected", current_selected)
                    timer.start()  # Start timer when question appears
                    try:
                        question = q[current_selected[0], current_selected[1]]['question']
                        current_answer = q[current_selected[0], current_selected[1]]['answer']
                        print("Question:", question)
                    except:
                        print('No Question Found For Position')
                    show_question_flag = False
                
                question_screen.show_question(question if 'question' in locals() else "")
                timer.update()  # Update timer state
                timer.draw(pygame.display.get_surface())  # Draw timer

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if event.pos[1] > 200:
                        if not showing_answer:
                            showing_answer = True
                            print("Selected Question", c, r, "Points:", board_matrix[c][r])
                        else:
                            mouse_pos = event.pos
                            if button_rects[0].collidepoint(mouse_pos):
                                team_scores[selected_team_index] += board_matrix[r][c]
                                correct = True
                            elif button_rects[1].collidepoint(mouse_pos):
                                team_scores[selected_team_index] -= board_matrix[r][c]
                                correct = False
                            elif button_rects[2].collidepoint(mouse_pos):
                                correct = None
                            
                            if button_rects[0].collidepoint(mouse_pos) or \
                            button_rects[1].collidepoint(mouse_pos) or \
                            button_rects[2].collidepoint(mouse_pos):
                                prev_scores = team_scores.copy()
                                prev_leader = max(range(len(team_scores)), key=lambda i: prev_scores[i])
                                
                                team_selected = False
                                question_time = False
                                pane1.draw_grid_flag = True
                                showing_answer = False
                                
                                if correct is not None:
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
