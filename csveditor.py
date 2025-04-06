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
                self.data.to_csv(self.csv_file, index=False)
                return True

            pygame.display.flip()
            clock.tick(30)

        return False