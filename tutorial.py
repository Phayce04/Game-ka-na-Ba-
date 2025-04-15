import pygame
import os, sys
import cv2

from utils import board_matrix, q, MAX_TIME_LIMIT, WIDTH, HEIGHT, white, grey, black, blue, red, green, yellow, clock

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class TutorialScreen:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.font = pygame.font.SysFont('Arial', 36)

        # Load video as background
        self.video = cv2.VideoCapture(resource_path('Larawan/tutorial.mp4'))

    def get_video_frame(self):
        ret, frame = self.video.read()
        if not ret or frame is None:
            self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop video
            ret, frame = self.video.read()
            if not ret or frame is None:
                return pygame.Surface((WIDTH, HEIGHT))  # Fallback
        frame = cv2.resize(frame, (WIDTH, HEIGHT))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return pygame.surfarray.make_surface(frame.swapaxes(0, 1))

    def show(self):
        running = True
        while running:
            # Draw video frame
            video_frame = self.get_video_frame()
            self.screen.blit(video_frame, (0, 0))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.video.release()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    running = False

            clock.tick(30)
