import pygame
import os, sys
import pandas as pd

from utils import board_matrix, q, MAX_TIME_LIMIT, WIDTH, HEIGHT, white, grey, black, blue, red, green, yellow, clock

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

        # Merged Header for Questions/Answers
        merged_qa_rect = pygame.Rect(0, 2 * self.cell_height + 5, self.cell_width * 5, self.cell_height)
        pygame.draw.rect(self.screen, (220, 220, 255), merged_qa_rect)
        pygame.draw.rect(self.screen, black, merged_qa_rect, 1)
        text = self.font.render("QUESTIONS / ANSWERS", True, black)
        text_rect = text.get_rect(center=merged_qa_rect.center)
        self.screen.blit(text, text_rect)

        # Header row
        for i, header in enumerate(headers):
            rect = pygame.Rect(i * self.cell_width, 3 * self.cell_height + 10 - self.scroll_offset,
                               self.cell_width, self.cell_height)
            pygame.draw.rect(self.screen, (200, 200, 200), rect)
            text = self.font.render(header, True, black)
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
                else:
                    cell_value = str(self.data.iloc[row_idx].get(col, ""))

                rect = pygame.Rect(col_idx * self.cell_width,
                                   4 * self.cell_height + 10 + row_idx * self.cell_height - self.scroll_offset,
                                   self.cell_width, self.cell_height)

                if self.selected_row == row_idx and self.selected_col == col_idx and col != "Score":
                    pygame.draw.rect(self.screen, (100, 200, 255), rect)
                else:
                    pygame.draw.rect(self.screen, white, rect)
                pygame.draw.rect(self.screen, black, rect, 1)

                text = self.font.render(cell_value[:20] + "..." if len(cell_value) > 20 else cell_value, True, black)
                self.screen.blit(text, (rect.x + 5, rect.y + 5))
    def is_valid_data(self):
        # Check for 5 non-empty categories
        category_vals = self.data["Categories"].dropna().astype(str).str.strip()
        if len(category_vals) < 5 or any(cat == "" for cat in category_vals[:5]):
            return False, "You must have 5 non-empty categories."

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
        merged_rect = pygame.Rect(0, 0, self.cell_width * 5, self.cell_height)
        pygame.draw.rect(self.screen, (180, 180, 250), merged_rect)
        pygame.draw.rect(self.screen, black, merged_rect, 1)
        text = self.font.render("CATEGORIES", True, black)
        text_rect = text.get_rect(center=merged_rect.center)
        self.screen.blit(text, text_rect)

        # Editable category row
        for i in range(5):
            cat_val = ""
            if i < len(self.data):
                cat_val = str(self.data.iloc[i].get("Categories", ""))

            cat_rect = pygame.Rect(i * self.cell_width, self.cell_height, self.cell_width, self.cell_height)
            pygame.draw.rect(self.screen, white, cat_rect)
            pygame.draw.rect(self.screen, blue if self.editing_category_col == i else black, cat_rect, 2)
            text = self.font.render(cat_val[:18] + "..." if len(cat_val) > 18 else cat_val, True, black)
            self.screen.blit(text, (cat_rect.x + 5, cat_rect.y + 5))
    def show_popup(self, message, duration=2000):
        # Store the current screen content to restore later
        screen_copy = self.screen.copy()
        
        # Create popup with dark blue background and gold text
        popup_rect = pygame.Rect(WIDTH // 4, HEIGHT // 3, WIDTH // 2, 100)
        pygame.draw.rect(self.screen, (0, 0, 139), popup_rect)  # Dark blue
        pygame.draw.rect(self.screen, (184, 134, 11), popup_rect, 2)  # Gold border

        text = self.font.render(message, True, (255, 215, 0))  # Gold text
        text_rect = text.get_rect(center=popup_rect.center)
        self.screen.blit(text, text_rect)
        pygame.display.update()

        # Pause to show the popup for given duration (ms)
        pygame.time.delay(duration)
        
        # Restore the original screen content
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

            save_btn = pygame.Rect(WIDTH - 150, 10, 140, 40)
            pygame.draw.rect(self.screen, green, save_btn)
            save_text = self.font.render("Save & Exit", True, white)
            self.screen.blit(save_text, (save_btn.x + 20, save_btn.y + 10))

            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()
            if save_btn.collidepoint(mouse_pos) and mouse_click[0]:
                valid, msg = self.is_valid_data()
                if valid:
                    self.data.to_csv(self.csv_file, index=False)
                    return True
                else:
                    self.show_popup(msg)

            pygame.display.flip()
            clock.tick(30)

        return False