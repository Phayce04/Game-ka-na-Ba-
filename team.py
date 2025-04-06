import pygame
import os, sys
import pandas as pd

from csveditor import CSVEditor
from tkinter import filedialog, Tk
from loadquestion import load_questions
from utils import board_matrix, q, MAX_TIME_LIMIT, WIDTH, HEIGHT, white, grey, black, blue, red, green, yellow, clock


class TeamSetupScreen:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.font_large = pygame.font.SysFont('Arial', 48)
        self.font_medium = pygame.font.SysFont('Arial', 36)
        self.font_small = pygame.font.SysFont('Arial', 24)
        self.team_count = 2
        self.team_inputs = []
        self.active_input = None
        
        # Add CSV control buttons
        self.csv_button = pygame.Rect(WIDTH//2 - 150, HEIGHT - 200, 300, 50)
        self.edit_button = pygame.Rect(WIDTH//2 - 150, HEIGHT - 130, 300, 50)
        self.done_button = pygame.Rect(WIDTH//2 - 100, HEIGHT - 60, 200, 50)
        
        self.current_csv = 'qset4_Book.csv'  # Default CSV file

    def show(self):
        running = True
        input_boxes = []
        
        while running:
            self.screen.fill(white)
            
            # Title
            title = self.font_large.render("Team Setup", True, blue)
            self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
            
            # Current CSV display
            csv_text = self.font_small.render(f"Using: {self.current_csv}", True, black)
            self.screen.blit(csv_text, (WIDTH//2 - csv_text.get_width()//2, 120))
            
            # CSV control buttons
            pygame.draw.rect(self.screen, grey, self.csv_button)
            csv_btn_text = self.font_medium.render("Change CSV", True, black)
            self.screen.blit(csv_btn_text, (self.csv_button.x + 50, self.csv_button.y + 10))
            
            pygame.draw.rect(self.screen, grey, self.edit_button)
            edit_btn_text = self.font_medium.render("Edit CSV", True, black)
            self.screen.blit(edit_btn_text, (self.edit_button.x + 70, self.edit_button.y + 10))
            
            # Team count controls
            count_text = self.font_medium.render("Number of Teams:", True, black)
            self.screen.blit(count_text, (WIDTH // 2 - 200, 150))
            
            minus_button = pygame.Rect(WIDTH // 2 + 50, 150, 50, 50)
            pygame.draw.rect(self.screen, red, minus_button)
            minus_text = self.font_medium.render("-", True, white)
            self.screen.blit(minus_text, (minus_button.x + 20, minus_button.y + 10))
            
            count_display = self.font_medium.render(str(self.team_count), True, black)
            self.screen.blit(count_display, (WIDTH // 2, 150))
            
            plus_button = pygame.Rect(WIDTH // 2 + 150, 150, 50, 50)
            pygame.draw.rect(self.screen, green, plus_button)
            plus_text = self.font_medium.render("+", True, white)
            self.screen.blit(plus_text, (plus_button.x + 20, plus_button.y + 10))
            
            # Team name inputs
            if len(self.team_inputs) != self.team_count:
                self.team_inputs = ["" for _ in range(self.team_count)]
                input_boxes = [pygame.Rect(WIDTH // 2 - 150, 250 + i * 60, 300, 40) for i in range(self.team_count)]
            
            for i, box in enumerate(input_boxes):
                label = self.font_small.render(f"Team {i+1}:", True, black)
                self.screen.blit(label, (box.x - 100, box.y + 10))
                
                color = blue if self.active_input == i else black
                pygame.draw.rect(self.screen, color, box, 2)
                
                text_surface = self.font_small.render(self.team_inputs[i], True, black)
                self.screen.blit(text_surface, (box.x + 5, box.y + 10))
            
            # Done button
            pygame.draw.rect(self.screen, green, self.done_button)
            done_text = self.font_medium.render("Start Game", True, white)
            self.screen.blit(done_text, (self.done_button.x + 20, self.done_button.y + 10))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.csv_button.collidepoint(event.pos):
                        self.select_csv_file()
                    elif self.edit_button.collidepoint(event.pos):
                        self.edit_csv_file()
                    # Check team count buttons
                    if minus_button.collidepoint(event.pos) and self.team_count > 1:
                        self.team_count -= 1
                    elif plus_button.collidepoint(event.pos) and self.team_count < 6:
                        self.team_count += 1
                    
                    # Check input boxes
                    self.active_input = None
                    for i, box in enumerate(input_boxes):
                        if box.collidepoint(event.pos):
                            self.active_input = i
                    
                    # Check done button
                    if self.done_button.collidepoint(event.pos):
                        if all(name.strip() != "" for name in self.team_inputs):
                            # Return the team names and scores to the caller
                            team_names = self.team_inputs
                            team_scores = [0] * self.team_count
                            return team_names, team_scores
                
                if event.type == pygame.KEYDOWN and self.active_input is not None:
                    if event.key == pygame.K_BACKSPACE:
                        self.team_inputs[self.active_input] = self.team_inputs[self.active_input][:-1]
                    else:
                        if len(self.team_inputs[self.active_input]) < 15:
                            self.team_inputs[self.active_input] += event.unicode
            
            pygame.display.flip()
            clock.tick(30)
    
    def select_csv_file(self):
        """Open file dialog to select CSV"""
        root = Tk()
        root.withdraw()  # Hide the main window
        file_path = filedialog.askopenfilename(
            title="Select Questions CSV",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file_path:
            self.current_csv = os.path.basename(file_path)
            # Reload questions
            global q, board_matrix
            try:
                load_questions(self.current_csv)
            except Exception as e:
                print(f"Error loading CSV: {e}")
    
    def edit_csv_file(self):
        """Open in-game CSV editor"""
        editor = CSVEditor(self.current_csv)
        editor.run()
        # Reload questions after editing
        load_questions(self.current_csv)
   

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = event.pos

                    # Detect category cell click
                    if self.cell_height <= y < 2 * self.cell_height:
                        col = x // self.cell_width
                        if 0 <= col < 5 and col < len(self.data):
                            self.editing_category_col = col
                            self.edit_text = str(self.data.iloc[col].get("Categories", ""))

                    else:
                        col = x // self.cell_width
                        row = (y + self.scroll_offset - (4 * self.cell_height + 10)) // self.cell_height

                        if 0 <= row < len(self.data) and 0 <= col < 5:
                            if col != 4:  # skip Score
                                self.selected_row = row
                                self.selected_col = col
                                self.editing_category_col = None
                                self.edit_text = str(self.data.iloc[row][["Row", "Col", "Question", "Answer"][col]])

                elif event.button == 4:
                    self.scroll_offset = max(0, self.scroll_offset - 20)
                elif event.button == 5:
                    self.scroll_offset += 20

            elif event.type == pygame.KEYDOWN:
                if self.selected_row is not None and self.selected_col is not None:
                    if event.key == pygame.K_RETURN:
                        col_name = ["Row", "Col", "Question", "Answer"][self.selected_col]
                        self.data.at[self.selected_row, col_name] = self.edit_text
                        self.data.to_csv(self.csv_file, index=False)
                        self.selected_row = None
                        self.selected_col = None
                    elif event.key == pygame.K_BACKSPACE:
                        self.edit_text = self.edit_text[:-1]
                    else:
                        self.edit_text += event.unicode

                elif self.editing_category_col is not None:
                    if event.key == pygame.K_RETURN:
                        self.data.at[self.editing_category_col, "Categories"] = self.edit_text
                        self.data.to_csv(self.csv_file, index=False)
                        self.editing_category_col = None
                    elif event.key == pygame.K_BACKSPACE:
                        self.edit_text = self.edit_text[:-1]
                    else:
                        self.edit_text += event.unicode

        return True
