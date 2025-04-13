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
        
        self.current_csv = 'default-na-tanong.csv'  # Default CSV file

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
                    elif plus_button.collidepoint(event.pos) and self.team_count < 4:
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
                        if (
                            len(self.team_inputs[self.active_input]) < 6
                            and event.unicode.isprintable()
                            and not event.unicode.isspace()
                        ):
                            self.team_inputs[self.active_input] += event.unicode

            
            pygame.display.flip()
            clock.tick(30)
    
    def select_csv_file(self):
        """Open file dialog to select and validate CSV"""
        root = Tk()
        root.withdraw()  # Hide the main window
        file_path = filedialog.askopenfilename(
            title="Select Questions CSV",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )

        if file_path:
            try:
                # Load and validate CSV
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

                # If all validations pass, load the questions
                self.current_csv = os.path.basename(file_path)
                global q, board_matrix
                q, board_matrix = load_questions(file_path)
                print("CSV loaded and validated successfully.")

            except Exception as e:
                print(f"Error loading CSV: {e}")
                self.show_popup(f"Invalid CSV:\n{e}")

    def show_popup(self, message, duration=2000):
        # Create a dark translucent background
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Popup box
        popup_rect = pygame.Rect(WIDTH // 4, HEIGHT // 3, WIDTH // 2, 120)
        pygame.draw.rect(self.screen, (0, 0, 139), popup_rect)  # Dark blue
        pygame.draw.rect(self.screen, (255, 215, 0), popup_rect, 3)  # Gold border

        font = pygame.font.SysFont("Arial", 24)
        lines = message.split("\n")
        for i, line in enumerate(lines):
            text = font.render(line, True, (255, 255, 255))
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 3 + 30 + i * 30))
            self.screen.blit(text, text_rect)

        pygame.display.update()
        pygame.time.delay(duration)

    
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
