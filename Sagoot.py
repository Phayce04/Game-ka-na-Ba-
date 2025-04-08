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

from pygame.locals import *




pygame.init()
answered_img = pygame.image.load("Larawan/trial.png")
answered_img = pygame.transform.scale(answered_img, (WIDTH // 6, 100))
pygame.mixer.init()
pygame.mixer.music.load('Tunog/trial.wav')
pygame.mixer.music.set_volume(0.3)  
pygame.mixer.music.play(-1) 
gameDisplay = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption('Bilis Sagot')
clock = pygame.time.Clock()

class Player(object):
    def __init__(self):
        self.score = 0
    def set_score(self,score):
        self.score = score
# WIDTH, HEIGHT = 1200,600

if not pygame.font: print ('Warning, fonts disabled')
if not pygame.mixer: print ('Warning, sound disabled')




class GameOverScreen:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.font_large = pygame.font.SysFont('Arial', 72)
        self.font_medium = pygame.font.SysFont('Arial', 48)
        self.font_small = pygame.font.SysFont('Arial', 36)
        
    def show(self):
        # Determine winning team(s)
        max_score = max(team_scores)
        winners = [i for i, score in enumerate(team_scores) if score == max_score]
        
        running = True
        while running:
            self.screen.fill(black)
            
            # Game Over title
            title = self.font_large.render("GAME OVER", True, yellow)
            self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
            
            # Display winner(s)
            if len(winners) == 1:
                winner_text = self.font_medium.render(f"Winner: {team_names[winners[0]]}!", True, green)
            else:
                # Handle tie
                winner_names = " & ".join([team_names[i] for i in winners])
                winner_text = self.font_medium.render(f"It's a tie! Winners: {winner_names}", True, green)
            
            self.screen.blit(winner_text, (WIDTH//2 - winner_text.get_width()//2, 250))
            
            # Display all scores
            score_title = self.font_medium.render("Final Scores:", True, white)
            self.screen.blit(score_title, (WIDTH//2 - score_title.get_width()//2, 350))
            
            for i, (name, score) in enumerate(zip(team_names, team_scores)):
                score_text = self.font_small.render(f"{name}: {score}", True, white)
                self.screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 420 + i*50))
            
            # Continue prompt
            continue_text = self.font_small.render("Click to return to home screen", True, yellow)
            if pygame.time.get_ticks() % 1000 < 500:  # Blinking effect
                self.screen.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT-100))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    running = False
                    self.reset_game()
            
            clock.tick(30)
    
    def reset_game(self):
        global p1, show_question_flag, start_flag, team_names, team_scores, already_selected
        global current_selected, team_selected, question_time, grid_drawn_flag
        global selected_team_index, show_timer_flag, Running_flag, game_state
        
        load_questions('qset4_Book.csv')  
        p1 = Player()
        show_question_flag = False
        start_flag = False
        team_names = []
        team_scores = []
        already_selected = []
        current_selected = [0,0]
        team_selected = False
        question_time = False
        grid_drawn_flag = False
        selected_team_index = -1
        show_timer_flag = False
        Running_flag = True
        game_state = "HOME"

# Initial game setup
GameOverScreen().reset_game()
class Pane(object):
    def __init__(self):
        self.font = pygame.font.SysFont('Arial', 18)
        pygame.display.set_caption('Box Test')
        self.screen = pygame.display.set_mode((WIDTH,HEIGHT), 0, 32)
        self.screen.fill((white))
        self.draw_grid_flag=True
        pygame.display.update()


    def draw_grid(self):
        if self.draw_grid_flag:
            self.screen.fill((white))    
            self.rect = pygame.draw.rect(self.screen, (blue), (0, 0, WIDTH, 100))
            self.draw_grid_flag=False
            self.show_score()
            self.show_selected_box()
        # pygame.display.update()

        cell_pos=WIDTH/6


        for row in range(6):
            cell_pos=WIDTH/6
            for x,header in enumerate(range(6)):
                self.rect = pygame.draw.rect(self.screen, (black), (0, row*100, cell_pos, 100),2)
                cell_pos+=WIDTH/6
                # pygame.display.update()
        pygame.display.update()

    def clear_already_selected(self, col, row):
        self.screen.blit(answered_img, (row*(WIDTH//6), col*100))

        
    def show_score(self):
        curser=10
        self.rect = pygame.draw.rect(self.screen, (grey), (0,600 , WIDTH, 100))
        for team in team_names:
            self.screen.blit(self.font.render(team, True, (255,0,0)), (curser, 610))
            curser+=WIDTH/6
        curser=10
        for score in team_scores:
            self.screen.blit(self.font.render(str(score), True, (255,0,0)), (curser, 640))
            curser+=WIDTH/6
    def show_selected_box(self):
        self.show_score()
        self.rect = pygame.draw.rect(self.screen, (red), (selected_team_index*(WIDTH/6),600 , WIDTH/6, 100),3)
        self.rect = pygame.draw.rect(self.screen, (red), (selected_team_index*(WIDTH/6),700 , WIDTH/6, 100))
        
    def addText(self,pos,text):
        # print(pos,text)
        x = pos[0]*WIDTH/6+10
        y= 100*pos[1]+35
        color = red
        # print('Y',y)
        if y<100:
            color=yellow
        self.screen.blit(self.font.render(str(text), True, color), (x, y))
        
class Question(object):
    def __init__(self):
        self.font = pygame.font.SysFont('Open Sans', 32)
        pygame.display.set_caption('Box Test')
        self.screen = pygame.display.set_mode((WIDTH,HEIGHT+200), 0, 32)
        self.screen.fill((white))
        pygame.display.update()

    def show(self,q):
        # curser=0
        self.rect = pygame.draw.rect(self.screen, (black), (0, 0, WIDTH, HEIGHT))
        sizeX, sizeY = self.font.size(q)
        if (sizeX>WIDTH):
            print("TEXT TOOO LONG!!!")
        print('SHOW QUESTION:',r,c)
        self.screen.blit(self.font.render(q, True, (255,0,0)), (WIDTH/2-(sizeX/2), HEIGHT/2))
        pygame.display.update()

    def show_answer(self,text):
        self.screen.fill((black))
        sizeX, sizeY = self.font.size(text)
        self.screen.blit(self.font.render(str(text), True, (255,0,0)), (WIDTH/2-(sizeX/2), HEIGHT/2))
        self.rect = pygame.draw.rect(self.screen, (green), ((WIDTH/6), 500, WIDTH/6, 100))
        self.rect = pygame.draw.rect(self.screen, (red), (4*(WIDTH/6), 500, WIDTH/6, 100))
        self.rect = pygame.draw.rect(self.screen, (grey), ((WIDTH/2)-(WIDTH/(18*2)), 500, WIDTH/18, 100))
        pygame.display.update()

class Timer(object):
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH,800), 0, 32)
        self.font = pygame.font.SysFont('Arial', 32)
        self.timer_x_pos=(WIDTH/2)-(WIDTH/12)
        self.timer_y_pos=WIDTH/6
        self.counter=0
        self.startTime=0
        self.elapsed=0

    def start(self):
        self.startTime = time.perf_counter()

    def show(self):
        self.elapsed = round(time.perf_counter()-self.startTime,1)
        self.rect = pygame.draw.rect(self.screen, (blue), (self.timer_x_pos, 500, self.timer_y_pos, 100))
        self.screen.blit(self.font.render(str(self.elapsed), True, (255,255,0)), (self.timer_x_pos+25,550))
        if self.elapsed >= MAX_TIME_LIMIT:
            pygame.mixer.music.load('Tunog/buzzer2.wav')
            pygame.mixer.music.play()
            timer.start()
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
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if exit_button_rect.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()
                    waiting = False
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
        
        if len(already_selected) == 10:  # 5 categories * 6 questions = 30
            game_state = "GAME_OVER"
            continue  
        
        while not question_time:
            r, c = 0, 0
            if not grid_drawn_flag:
                pane1.draw_grid()
                for i in range(6):
                    for j in range(6):
                        pane1.addText((i,j), board_matrix[j][i])
                grid_drawn_flag = True

            for each_already_selected in already_selected:
                pane1.clear_already_selected(each_already_selected[0], each_already_selected[1])
            
            draw_exit_button(pygame.display.get_surface())
            
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
                        for col in range(7): 
                            if col * (WIDTH / 6) < event.pos[0] < (col + 1) * (WIDTH / 6):
                                c = col
                                for row in range(6):
                                    if row * (HEIGHT / 6) < event.pos[1] < (row + 1) * (HEIGHT / 6):
                                        r = row + 1
                                        print('Clicked on:', r, c, 'SCORE:', board_matrix[r][c])
                                        show_question_flag = True
                                        if (r, c) not in already_selected:
                                            already_selected.append((r, c))
                                            current_selected = [r, c]
                                            question_time = True
                                        else:
                                            print('Already selected')
                    else:
                        print('First select a team')
                        for col in range(6):
                            if col < len(team_names) and col * (WIDTH / 6) < event.pos[0] < (col + 1) * (WIDTH / 6) and event.pos[1] > 600:
                                print('Selected Team:', col, 'Selected Team Name:', team_names[col], 'score', team_scores[col])
                                selected_team_index = col
                                pane1.show_selected_box()
                                team_selected = True
                            else:
                                print("Clicked on empty spot, no team here!")

            pygame.display.update()
            clock.tick(60)

        while question_time:
            grid_drawn_flag = False
            if show_timer_flag:
                timer.show()
            if show_question_flag:
                print("Current Selected", current_selected)
                timer.start()
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
                    
                    if event.pos[1] < 600:
                        if event.pos[0] > 500 and event.pos[0] < 700 and show_timer_flag:
                            print('Timer')
                            timer.start()
                            break
                        click_count += 1
                        print(q[r, c]['answer'])
                        question_screen.show_answer(q[r, c]['answer'])
                        show_timer_flag = False
                        print("Selected Question", c, r, "Points:", board_matrix[c][r], 'Click Count:', click_count)
                        print("Question Time")
                        if click_count == 2:
                            if event.pos[0] > (WIDTH / 6) and event.pos[0] < 2 * (WIDTH / 6):
                                print("RIGHTTTTT")
                                team_scores[selected_team_index] = team_scores[selected_team_index] + board_matrix[r][c]
                            elif event.pos[0] > 4 * (WIDTH / 6) and event.pos[0] < 5 * (WIDTH / 6):
                                print('WRONGGGG!')
                                team_scores[selected_team_index] = team_scores[selected_team_index] - board_matrix[r][c]
                            print('Second Click:', event.pos[0], event.pos[1])
                            team_selected = False
                            question_time = False
                            pane1.draw_grid_flag = True
                            click_count = 0
                    else:
                        print('NEW TEAM SELECT MODE!')
                        for col in range(6):
                            if col * (WIDTH / 6) < event.pos[0] < (col + 1) * (WIDTH / 6) and event.pos[1] > 600:
                                if col < len(team_names):
                                    print('New Selected Team:', col, 'Selected Team Name:', team_names[col], 'score', team_scores[col])
                                    team_scores[selected_team_index] = team_scores[selected_team_index] - board_matrix[r][c]
                                    selected_team_index = col
                                    pane1.show_score()
                                    pane1.show_selected_box()
                                    timer.start()
            
            pygame.display.update()
            clock.tick(60)
    
    elif game_state == "GAME_OVER":
        game_over = GameOverScreen()
        game_over.show()
        draw_exit_button(pygame.display.get_surface())
        draw_restart_button(pygame.display.get_surface())
        pygame.display.update()
        
        # Wait for click to either restart or exit
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if exit_button_rect.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()
                    if restart_button_rect.collidepoint(event.pos):
                        GameOverScreen().reset_game()
                        waiting = False
                        break
                    waiting = False