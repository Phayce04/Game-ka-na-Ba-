import pygame
import sys

board_matrix=[
              ["First","Second","Third","Fourth","Fifth","Sixth"],
              [200,200,200,200,200,200],
              [400,400,400,400,400,400],
              [600,600,600,600,600,600],
              [800,800,800,800,800,800],
              [1000,1000,1000,1000,1000,1000]
              ]
q={}
MAX_TIME_LIMIT = 10

pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
white = (255,255,255)
grey = (160,160,160)
black = (0,0,0)
blue = (0,0,255)
red = (255,0,0)
green = (0,255,0)
yellow = (255,255,0)
clock = pygame.time.Clock()