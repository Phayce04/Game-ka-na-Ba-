import pygame
import os, sys
import pandas as pd

from utils import board_matrix, q, MAX_TIME_LIMIT, WIDTH, HEIGHT, white, grey, black, blue, red, green, yellow, clock
jeopardy_yellow = (238, 202, 62)  # EECA3E
jeopardy_gold = (184, 134, 11)    # B8860B
jeopardy_dark_blue = (0, 0, 139)  # Dark blue
jeopardy_blue = (8, 32, 128)      # A nice Jeopardy blue
class CSVEditor:
    def __init__(self, csv_file):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.font = pygame.font.SysFont('Arial', 24)
        self.csv_file = csv_file
        self.data = pd.read_csv(csv_file)
        self.editing_cell = None
        self.edit_text = ""
        self.scroll_offset = 0
        self.cell_width = WIDTH // 6
        self.cell_height = 40
        self.selected_row = None
        self.selected_col = None
        self.editing_category_col = None  # NEW: for editing category

    def draw_table(self):
        headers = ["Row", "Col", "Question", "Answer", "Score"]
        total_headers = len(headers)
        stretched_cell_width = WIDTH // total_headers

        # Merged Header for Questions/Answers - dark blue with gold border
        merged_qa_rect = pygame.Rect(0, 2 * self.cell_height + 5, WIDTH, self.cell_height)
        pygame.draw.rect(self.screen, jeopardy_dark_blue, merged_qa_rect)
        pygame.draw.rect(self.screen, jeopardy_gold, merged_qa_rect, 2)
        text = self.font.render("QUESTIONS / ANSWERS", True, white)
        text_rect = text.get_rect(center=merged_qa_rect.center)
        self.screen.blit(text, text_rect)

        # Header row - dark blue with gold divisions
        for i, header in enumerate(headers):
            rect = pygame.Rect(i * stretched_cell_width, 3 * self.cell_height + 10 - self.scroll_offset,
                            stretched_cell_width, self.cell_height)
            # Make Score header yellow, others dark blue
            if header == "Score":
                pygame.draw.rect(self.screen, jeopardy_yellow, rect)
                text_color = black  # Black text on yellow
            else:
                pygame.draw.rect(self.screen, jeopardy_dark_blue, rect)
                text_color = white  # White text on dark blue
                
            pygame.draw.rect(self.screen, jeopardy_gold, rect, 1)  # Gold border
            text = self.font.render(header, True, text_color)
            self.screen.blit(text, (rect.x + 5, rect.y + 5))

        # Data rows
        for row_idx in range(len(self.data)):
            for col_idx, col in enumerate(headers):
                if col == "Score":
                    try:
                        r = int(self.data.iloc[row_idx]["Row"])
                        c = int(self.data.iloc[row_idx]["Col"])
                        cell_value = str(board_matrix[r][c])
                    except:
                        cell_value = "N/A"
                    
                    # Score column - yellow background
                    rect = pygame.Rect(col_idx * stretched_cell_width,
                                    4 * self.cell_height + 10 + row_idx * self.cell_height - self.scroll_offset,
                                    stretched_cell_width, self.cell_height)
                    pygame.draw.rect(self.screen, jeopardy_yellow, rect)
                    text_color = black  # Black text on yellow
                else:
                    cell_value = str(self.data.iloc[row_idx].get(col, ""))
                    rect = pygame.Rect(col_idx * stretched_cell_width,
                                    4 * self.cell_height + 10 + row_idx * self.cell_height - self.scroll_offset,
                                    stretched_cell_width, self.cell_height)
                    # White background for other cells
                    pygame.draw.rect(self.screen, white, rect)
                    text_color = black  # Black text on white

                # Highlight selected cell (except Score column)
                if self.selected_row == row_idx and self.selected_col == col_idx and col != "Score":
                    pygame.draw.rect(self.screen, (100, 200, 255), rect)  # Light blue selection
                
                # Dark blue divisions between cells
                pygame.draw.rect(self.screen, jeopardy_dark_blue, rect, 1)

                text = self.font.render(cell_value[:20] + "..." if len(cell_value) > 20 else cell_value, True, text_color)
                self.screen.blit(text, (rect.x + 5, rect.y + 5))
    def is_valid_data(self):
        # Check for 6 non-empty categories
        category_vals = self.data["Categories"].dropna().astype(str).str.strip()
        if len(category_vals) < 6 or any(cat == "" for cat in category_vals[:6]):
            return False, "You must have 6 non-empty categories."

        required_coords = {(r, c) for r in range(1, 6) for c in range(6)}
        actual_coords = set()

        for i, row in self.data.iterrows():
            try:
                r = int(row["Row"])
                c = int(row["Col"])
            except:
                return False, f"Row {r}: 'Row' and 'Col' must be integers."

            if not (1 <= r <= 5):
                return False, f"Row {r}: 'Row' must be between 1 and 5 (got {r})."
            if not (0 <= c <= 5):
                return False, f"Row {r}: 'Col' must be between 0 and 5 (got {c})."

            q_text = str(row.get("Question", "")).strip()
            a_text = str(row.get("Answer", "")).strip()

            if q_text == "" or q_text.lower() == "nan":
                return False, f"Row {r}, Col {c}: Question is empty."
            if a_text == "" or a_text.lower() == "nan":
                return False, f"Row {r}, Col {c}: Answer is empty."

            actual_coords.add((r, c))

        if actual_coords != required_coords:
            missing = sorted(list(required_coords - actual_coords))
            return False, f"Missing Q/A at {missing[0]} (row {missing[0][0]}, col {missing[0][1]})."

        return True, ""


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
                        if 0 <= col < 6 and col < len(self.data):
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
                        self.data.at[self.selected_row, col_name] = self.edit_text.strip()
                        valid, msg = self.is_valid_data()
                        if valid:
                            self.data.to_csv(self.csv_file, index=False)
                        else:
                            print("Validation failed:", msg)

                        self.selected_row = None
                        self.selected_col = None
                    elif event.key == pygame.K_BACKSPACE:
                        self.edit_text = self.edit_text[:-1]
                    else:
                        self.edit_text += event.unicode

                elif self.editing_category_col is not None:
                    if event.key == pygame.K_RETURN:
                        self.data.at[self.editing_category_col, "Categories"] = self.edit_text.strip()
                        self.data.to_csv(self.csv_file, index=False)
                        self.editing_category_col = None
                    elif event.key == pygame.K_BACKSPACE:
                        self.edit_text = self.edit_text[:-1]
                    else:
                        self.edit_text += event.unicode

        return True

    def draw_edit_box(self):
        if self.selected_row is not None and self.selected_col is not None or self.editing_category_col is not None:
            edit_rect = pygame.Rect(50, HEIGHT - 100, WIDTH - 100, 50)
            pygame.draw.rect(self.screen, white, edit_rect)
            pygame.draw.rect(self.screen, blue, edit_rect, 2)

            editing_label = "Editing category" if self.editing_category_col is not None else "Editing cell"
            text = self.font.render(f"{editing_label}: {self.edit_text}", True, black)
            self.screen.blit(text, (edit_rect.x + 10, edit_rect.y + 15))

    def draw_categories_table(self):
        if "Categories" not in self.data.columns:
            return

        # Merged header row for "CATEGORIES"
        merged_rect = pygame.Rect(0, 0, self.cell_width * 6, self.cell_height)
        pygame.draw.rect(self.screen, jeopardy_dark_blue, merged_rect)
        pygame.draw.rect(self.screen, jeopardy_gold, merged_rect, 2)
        text = self.font.render("CATEGORIES", True, white)
        text_rect = text.get_rect(center=merged_rect.center)
        self.screen.blit(text, text_rect)

        # Editable category row - using jeopardy_yellow
        for i in range(6):
            cat_val = ""
            if i < len(self.data):
                cat_val = str(self.data.iloc[i].get("Categories", ""))

            cat_rect = pygame.Rect(i * self.cell_width, self.cell_height, self.cell_width, self.cell_height)
            pygame.draw.rect(self.screen, jeopardy_yellow, cat_rect)
            pygame.draw.rect(self.screen, jeopardy_gold if self.editing_category_col == i else jeopardy_dark_blue, cat_rect, 2)
            text = self.font.render(cat_val[:18] + "..." if len(cat_val) > 18 else cat_val, True, black)
            self.screen.blit(text, (cat_rect.x + 5, cat_rect.y + 5))
    def show_popup(self, message, duration=2000):
        screen_copy = self.screen.copy()
        
        popup_rect = pygame.Rect(WIDTH // 4, HEIGHT // 3, WIDTH // 2, 100)
        pygame.draw.rect(self.screen, jeopardy_dark_blue, popup_rect)
        pygame.draw.rect(self.screen, jeopardy_gold, popup_rect, 3)  # Thicker gold border

        text = self.font.render(message, True, white)  # White text for better contrast
        text_rect = text.get_rect(center=popup_rect.center)
        self.screen.blit(text, text_rect)
        pygame.display.update()

        pygame.time.delay(duration)
        
        self.screen.blit(screen_copy, (0, 0))
        pygame.display.update()
    def run(self):
        running = True
        while running:
            self.screen.fill(white)
            running = self.handle_events()

            self.draw_categories_table()
            self.draw_table()
            self.draw_edit_box()

            # Save button styling
            save_btn = pygame.Rect(WIDTH//2 - 100, HEIGHT - 60, 200, 50)
            pygame.draw.rect(self.screen, jeopardy_blue, save_btn)  # Using the jeopardy blue
            pygame.draw.rect(self.screen, jeopardy_gold, save_btn, 3)  # Gold border
            save_text = self.font.render("SAVE & EXIT", True, white)  # White text
            
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()
            if save_btn.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, jeopardy_dark_blue, save_btn)  # Darker on hover
                pygame.draw.rect(self.screen, jeopardy_yellow, save_btn, 3)  # Yellow border on hover
                if mouse_click[0]:
                    valid, msg = self.is_valid_data()
                    if valid:
                        self.data.to_csv(self.csv_file, index=False)
                        return True
                    else:
                        self.show_popup(msg)
            
            self.screen.blit(save_text, (save_btn.x + 30, save_btn.y + 15))
            pygame.display.flip()
            clock.tick(30)

        return False