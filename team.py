import pygame
import os, sys
import pandas as pd
import cv2

from csveditor import CSVEditor
from tkinter import filedialog, Tk
from loadquestion import load_questions
from utils import board_matrix, q, MAX_TIME_LIMIT, WIDTH, HEIGHT, white, grey, black, blue, red, green, yellow, clock

class CSVSetupScreen:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        
        # Font loading with arcade font
        try:
            self.font_small = pygame.font.Font("Fonts/ARCADE_N.TTF", 36)
        except:
            self.font_small = pygame.font.SysFont('Arial', 24)
        
        # Video background setup
        self.video_capture = cv2.VideoCapture("Larawan/csv.mp4")
        self.video_fps = self.video_capture.get(cv2.CAP_PROP_FPS)
        
        # Button rectangles
        self.csv_button = pygame.Rect(WIDTH//2 - 320, HEIGHT//2 -60, 650, 140)
        self.edit_button = pygame.Rect(WIDTH//2 - 320, HEIGHT//2 + 100, 650, 140)
        
        # Navigation buttons
        self.next_button = pygame.Rect(WIDTH - 150, 20, 120, 120)  # Top right
        self.prev_button = pygame.Rect(30, 20, 120, 120)  # Top left
        
        # Store full path to default CSV
        self.current_csv = os.path.abspath('Katanungan/default-na-tanong.csv')

    def get_video_frame(self):
        ret, frame = self.video_capture.read()
        if not ret or frame is None:
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.video_capture.read()
            if not ret or frame is None:
                return pygame.Surface((WIDTH, HEIGHT))
        frame = cv2.resize(frame, (WIDTH, HEIGHT))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return pygame.surfarray.make_surface(frame.swapaxes(0, 1))

    def show(self):
        running = True
        
        while running:
            # Draw video background
            video_frame = self.get_video_frame()
            self.screen.blit(video_frame, (0, 0))
            
            # Display just the filename for cleaner UI
            csv_filename = os.path.basename(self.current_csv)
            csv_display = f"Kasalukuyang Katanungan: {csv_filename}"
            csv_text = self.font_small.render(csv_display, True, (238, 202, 62))  # Gold color
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
            clock.tick(self.video_fps if self.video_fps > 0 else 30)
    def __del__(self):
        """Clean up video resources"""
        self.video_capture.release()
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
        
        # Load fonts
        try:
            self.font_large = pygame.font.Font("Fonts/ArchivoBlack-Regular.ttf", 72)
            self.font_medium = pygame.font.Font("Fonts/ArchivoBlack-Regular.ttf", 48)
            self.font_small = pygame.font.Font("Fonts/ArchivoBlack-Regular.ttf", 36)
            self.font_thin = pygame.font.Font("Fonts/ArchivoBlack-Regular.ttf", 24)
        except:
            self.font_large = pygame.font.SysFont('Arial', 72, bold=True)
            self.font_medium = pygame.font.SysFont('Arial', 48, bold=True)
            self.font_small = pygame.font.SysFont('Arial', 36, bold=True)
            self.font_thin = pygame.font.SysFont('Arial', 24, bold=True)
        
        # Team setup variables
        self.team_count = 2
        self.team_inputs = []
        self.active_input = None
        
        # Load background images
        self.background = pygame.image.load("Larawan/pangkat.png")
        self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))
        self.team_bg = pygame.image.load('Larawan/Bg5.png').convert()
        
        # Colors
        self.gold_color = (212, 175, 55)
        self.name_color = (238, 202, 62)
        self.white = (255, 255, 255)
        
        # Navigation buttons
        self.prev_button = pygame.Rect(20, 20, 130, 60)
        self.done_button = pygame.Rect(WIDTH - 210, HEIGHT - 90, 180, 60)

    def show(self):
        running = True
        input_boxes = []
        
        while running:
            self.screen.blit(self.background, (0, 0))
            
            # Team count controls (unchanged positions)
            center_x = WIDTH // 2
            button_y = 375

            # Minus button (unchanged)
            minus_radius = 50
            minus_button_pos = (center_x + 190, button_y)
            s = pygame.Surface((minus_radius*2, minus_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (200, 0, 0, 180), (minus_radius, minus_radius), minus_radius)
            self.screen.blit(s, (minus_button_pos[0] - minus_radius, minus_button_pos[1] - minus_radius))

            # Team count display (unchanged)
            count_display = self.font_large.render(str(self.team_count), True, (238, 202, 62))
            self.screen.blit(count_display, ((center_x + 375) - count_display.get_width() // 2 -15, button_y - count_display.get_height() // 2))

            # Plus button (unchanged)
            plus_radius = 50
            plus_button_pos = (center_x + 540, button_y)
            s = pygame.Surface((plus_radius*2, plus_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (0, 200, 0, 180), (plus_radius, plus_radius), plus_radius)
            self.screen.blit(s, (plus_button_pos[0] - plus_radius, plus_button_pos[1] - plus_radius))
            
            # Team name inputs - with larger boxes and 6-character limit
            if len(self.team_inputs) != self.team_count:
                self.team_inputs = ["" for _ in range(self.team_count)]
            
            # Larger boxes with adjusted spacing
            gap_x = 100 if self.team_count == 2 else 30 if self.team_count == 4 else 80
            column_width = 350  # Increased from 285
            box_height = 180   # Increased from 140
            total_width = (column_width + gap_x) * self.team_count - gap_x
            start_x = WIDTH // 2 - total_width // 2
            y_offset = 500  # Same vertical position
            
            for i in range(self.team_count):
                x = start_x + i * (column_width + gap_x)
                
                # Draw larger team background
                team_bg_scaled = pygame.transform.scale(self.team_bg, (column_width, box_height))
                self.screen.blit(team_bg_scaled, (x, y_offset))
                
                # Team label
                label = self.font_small.render(f"TEAM {i+1}", True, self.name_color)
                self.screen.blit(label, (x + (column_width - label.get_width())//2, y_offset + 25))  # Adjusted position
                
                # Larger input box
                input_rect = pygame.Rect(x + 25, y_offset + 75, column_width - 50, 60)  # Increased size
                
                # Draw input background
                s = pygame.Surface((input_rect.width, input_rect.height), pygame.SRCALPHA)
                s.fill((255, 255, 255, 128))
                self.screen.blit(s, (input_rect.x, input_rect.y))
                
                # Draw border if active
                border_color = self.name_color if self.active_input == i else self.white
                pygame.draw.rect(self.screen, border_color, input_rect, 2)
                
                # Draw input text (limited to 6 characters)
                display_text = self.team_inputs[i][:6]  # Truncate to 6 chars
                text_surface = self.font_small.render(display_text, True, (0, 0, 0))
                self.screen.blit(text_surface, (input_rect.x + 10, input_rect.y + 15))
                
                # Draw gold border around entire team box
                pygame.draw.rect(self.screen, self.gold_color, (x, y_offset, column_width, box_height), 8)
                
                # Store the input rect for click detection
                if len(input_boxes) <= i:
                    input_boxes.append(input_rect)
                else:
                    input_boxes[i] = input_rect
            
            # Previous button (unchanged)
            s = pygame.Surface((self.prev_button.width, self.prev_button.height), pygame.SRCALPHA)
            s.fill((200, 100, 100, 128))
            self.screen.blit(s, (self.prev_button.x, self.prev_button.y))

            # Start button (unchanged)
            s = pygame.Surface((self.done_button.width, self.done_button.height), pygame.SRCALPHA)
            s.fill((100, 200, 100, 180))
            self.screen.blit(s, (self.done_button.x, self.done_button.y))
            
            # Event handling with 6-character limit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Check team count buttons
                    if ((mouse_pos[0] - minus_button_pos[0])**2 + 
                        (mouse_pos[1] - minus_button_pos[1])**2 <= minus_radius**2 and 
                        self.team_count > 1):
                        self.team_count -= 1
                    elif ((mouse_pos[0] - plus_button_pos[0])**2 + 
                         (mouse_pos[1] - plus_button_pos[1])**2 <= plus_radius**2 and 
                         self.team_count < 4):
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
                        if (len(self.team_inputs[self.active_input]) < 6 and  # Changed from 12 to 6
                           event.unicode.isprintable() and 
                           not event.unicode.isspace()):
                            self.team_inputs[self.active_input] += event.unicode

            pygame.display.flip()
            clock.tick(30)