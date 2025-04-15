import pygame
import os, sys
import pandas as pd

from csveditor import CSVEditor
from tkinter import filedialog, Tk
from loadquestion import load_questions
from utils import board_matrix, q, MAX_TIME_LIMIT, WIDTH, HEIGHT, white, grey, black, blue, red, green, yellow, clock

class CSVSetupScreen:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        
        # Font loading with fallback
        try:
            self.font_small = pygame.font.Font("Fonts/ArchivoBlack-Regular.ttf", 36)
        except:
            self.font_small = pygame.font.SysFont('Arial', 24)
        
        # Background setup
        self.background = pygame.image.load("Larawan/question.png")
        self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))
        
        # Button rectangles
        self.csv_button = pygame.Rect(WIDTH//2 - 320, HEIGHT//2 -60, 650, 140)
        self.edit_button = pygame.Rect(WIDTH//2 - 320, HEIGHT//2 + 100, 650, 140)
        
        # Navigation buttons
        self.next_button = pygame.Rect(WIDTH - 150, 20, 120, 120)  # Top right
        self.prev_button = pygame.Rect(30, 20, 120, 120)  # Top left
        
        # Store full path to default CSV
        self.current_csv = os.path.abspath('default-na-tanong.csv')

    def show(self):
        running = True
        
        while running:
            self.screen.blit(self.background, (0, 0))
            
            # Display just the filename for cleaner UI
            csv_filename = os.path.basename(self.current_csv)
            csv_display = f"Kasalukuyang Katanungan: {csv_filename}"
            csv_text = self.font_small.render(csv_display, True, (238, 202, 62))  
            self.screen.blit(csv_text, (WIDTH//2 - csv_text.get_width()//2, 250))
            
            # Draw translucent buttons
            buttons = [
                (self.csv_button, (150, 150, 150, 128)),
                (self.edit_button, (150, 150, 150, 128)),
                (self.next_button, (100, 200, 100, 128)),  # Green
                (self.prev_button, (200, 100, 100, 128))   # Red
            ]
            
            for rect, color in buttons:
                s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                s.fill(color)
                self.screen.blit(s, (rect.x, rect.y))
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.csv_button.collidepoint(event.pos):
                        self.select_csv_file()
                    elif self.edit_button.collidepoint(event.pos):
                        self.edit_csv_file()
                    elif self.next_button.collidepoint(event.pos):
                        return "NEXT"
                    elif self.prev_button.collidepoint(event.pos):
                        return "PREVIOUS"
            
            pygame.display.flip()
            clock.tick(30)

    def select_csv_file(self):
        """Open file dialog to select and validate CSV"""
        root = Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title="Select Questions CSV",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )

        if file_path:
            try:
                # Validate CSV structure
                df = pd.read_csv(file_path)
                required_cols = {"Row", "Col", "Question", "Answer", "Categories"}
                missing = required_cols - set(df.columns)
                if missing:
                    raise ValueError(f"Missing required columns: {', '.join(missing)}")

                # Validate categories
                categories = df["Categories"].dropna().astype(str).str.strip().tolist()
                if len(categories) < 6 or any(cat == "" for cat in categories[:6]):
                    raise ValueError("There must be at least 6 non-empty categories in the 'Categories' column.")

                # Validate Q/A structure
                required_coords = {(r, c) for r in range(1, 6) for c in range(6)}
                actual_coords = set()

                for i, row in df.iterrows():
                    try:
                        r = int(row["Row"])
                        c = int(row["Col"])
                    except:
                        raise ValueError(f"Row {i+1}: Row and Col must be integers.")

                    if not (1 <= r <= 5):
                        raise ValueError(f"Row {i+1}: Row must be between 1 and 5.")
                    if not (0 <= c <= 5):
                        raise ValueError(f"Row {i+1}: Col must be between 0 and 5.")

                    q_text = str(row.get("Question", "")).strip()
                    a_text = str(row.get("Answer", "")).strip()

                    if not q_text or q_text.lower() == "nan":
                        raise ValueError(f"Row {i+1}, Col {c}: Question is empty.")
                    if not a_text or a_text.lower() == "nan":
                        raise ValueError(f"Row {i+1}, Col {c}: Answer is empty.")

                    actual_coords.add((r, c))

                if actual_coords != required_coords:
                    missing = sorted(list(required_coords - actual_coords))
                    raise ValueError(f"Missing Q/A at row {missing[0][0]}, col {missing[0][1]}.")

                # Store full path and load questions
                self.current_csv = os.path.abspath(file_path)
                global q, board_matrix
                q, board_matrix = load_questions(self.current_csv)
                print(f"CSV loaded successfully from: {self.current_csv}")

            except Exception as e:
                print(f"Error loading CSV: {e}")
                self.show_popup(f"Invalid CSV:\n{e}")

    def show_popup(self, message, duration=2000):
        """Display a temporary popup message"""
        # Create overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Popup box
        popup_rect = pygame.Rect(WIDTH // 4, HEIGHT // 3, WIDTH // 2, 120)
        pygame.draw.rect(self.screen, (0, 0, 139), popup_rect)  # Dark blue
        pygame.draw.rect(self.screen, (255, 215, 0), popup_rect, 3)  # Gold border

        # Render message
        font = pygame.font.SysFont("Arial", 24)
        lines = message.split("\n")
        for i, line in enumerate(lines):
            text = font.render(line, True, (255, 255, 255))
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 3 + 30 + i * 30))
            self.screen.blit(text, text_rect)

        pygame.display.update()
        pygame.time.delay(duration)

    def edit_csv_file(self):
        """Open the CSV editor with the current file"""
        try:
            editor = CSVEditor(self.current_csv)
            editor.run()
            # Reload questions after editing
            load_questions(self.current_csv)
        except Exception as e:
            print(f"Error editing CSV: {e}")
            self.show_popup(f"Failed to edit CSV:\n{e}")

class TeamSetupScreen:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.font_large = pygame.font.SysFont('Arial', 48)
        self.font_medium = pygame.font.SysFont('Arial', 36)
        self.font_small = pygame.font.SysFont('Arial', 24)
        self.team_count = 2
        self.team_inputs = []
        self.active_input = None
        
        # Navigation button (only previous needed)
        self.prev_button = pygame.Rect(30, 20, 120, 120)  # Top left (red)
        self.done_button = pygame.Rect(WIDTH//2 - 100, HEIGHT - 100, 200, 50)  # Start Game button

    def show(self):
        running = True
        input_boxes = []
        
        while running:
            self.screen.fill(white)
            
            # Title
            title = self.font_large.render("Team Setup", True, blue)
            self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
            
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
            
            # Previous button (translucent red)
            s = pygame.Surface((self.prev_button.width, self.prev_button.height), pygame.SRCALPHA)
            s.fill((200, 100, 100, 128))  # Translucent red
            self.screen.blit(s, (self.prev_button.x, self.prev_button.y))
            
            # Start Game button
            pygame.draw.rect(self.screen, green, self.done_button)
            done_text = self.font_medium.render("Start Game", True, white)
            self.screen.blit(done_text, (self.done_button.x + 20, self.done_button.y + 10))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Check team count buttons
                    if minus_button.collidepoint(event.pos) and self.team_count > 1:
                        self.team_count -= 1
                    elif plus_button.collidepoint(event.pos) and self.team_count < 4:
                        self.team_count += 1
                    
                    # Check input boxes
                    self.active_input = None
                    for i, box in enumerate(input_boxes):
                        if box.collidepoint(event.pos):
                            self.active_input = i
                    
                    # Check previous button
                    if self.prev_button.collidepoint(event.pos):
                        return "PREVIOUS", None, None
                    
                    # Check Start Game button
                    if self.done_button.collidepoint(event.pos):
                        if all(name.strip() != "" for name in self.team_inputs):
                            return "NEXT", self.team_inputs, [0] * self.team_count
                
                if event.type == pygame.KEYDOWN and self.active_input is not None:
                    if event.key == pygame.K_BACKSPACE:
                        self.team_inputs[self.active_input] = self.team_inputs[self.active_input][:-1]
                    else:
                        if (len(self.team_inputs[self.active_input]) < 6 and 
                           event.unicode.isprintable() and 
                           not event.unicode.isspace()):
                            self.team_inputs[self.active_input] += event.unicode

            pygame.display.flip()
            clock.tick(30)