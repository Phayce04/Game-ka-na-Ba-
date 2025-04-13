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
        
        # Ensure numeric columns stay numeric
        self.data['Row'] = pd.to_numeric(self.data['Row'], errors='coerce').fillna(1).astype(int)
        self.data['Col'] = pd.to_numeric(self.data['Col'], errors='coerce').fillna(0).astype(int)
        
        # Selection and editing state
        self.selected_row = None
        self.selected_col = None
        self.editing_category_col = None
        self.edit_text = ""
        self.cursor_pos = 0
        self.selection_start = None
        self.selection_end = None
        self.cursor_visible = True
        self.cursor_blink_time = 0
        self.selection_anchor = None  # For tracking selection start position
        self.dragging = False
        # UI dimensions
        self.scroll_offset = 0
        self.cell_width = WIDTH // 6
        self.cell_height = 40
        
        # Initialize clipboard
        pygame.scrap.init()
        pygame.scrap.set_mode(pygame.SCRAP_CLIPBOARD)
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
    def draw_table(self):
        headers = ["Row", "Col", "Question", "Answer", "Score"]
        total_headers = len(headers)
        stretched_cell_width = WIDTH // total_headers

        # Merged Header for Questions/Answers
        merged_qa_rect = pygame.Rect(0, 2 * self.cell_height + 5, WIDTH, self.cell_height)
        pygame.draw.rect(self.screen, jeopardy_dark_blue, merged_qa_rect)
        pygame.draw.rect(self.screen, jeopardy_gold, merged_qa_rect, 2)
        text = self.font.render("QUESTIONS / ANSWERS", True, white)
        text_rect = text.get_rect(center=merged_qa_rect.center)
        self.screen.blit(text, text_rect)

        # Header row
        for i, header in enumerate(headers):
            rect = pygame.Rect(i * stretched_cell_width, 3 * self.cell_height + 10 - self.scroll_offset,
                            stretched_cell_width, self.cell_height)
            if header == "Score":
                pygame.draw.rect(self.screen, jeopardy_yellow, rect)
                text_color = black
            else:
                pygame.draw.rect(self.screen, jeopardy_dark_blue, rect)
                text_color = white
                
            pygame.draw.rect(self.screen, jeopardy_gold, rect, 1)
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
                    
                    rect = pygame.Rect(col_idx * stretched_cell_width,
                                    4 * self.cell_height + 10 + row_idx * self.cell_height - self.scroll_offset,
                                    stretched_cell_width, self.cell_height)
                    pygame.draw.rect(self.screen, jeopardy_yellow, rect)
                    text_color = black
                else:
                    cell_value = str(self.data.iloc[row_idx].get(col, ""))
                    rect = pygame.Rect(col_idx * stretched_cell_width,
                                    4 * self.cell_height + 10 + row_idx * self.cell_height - self.scroll_offset,
                                    stretched_cell_width, self.cell_height)
                    pygame.draw.rect(self.screen, white, rect)
                    text_color = black

                # Highlight selected cell
                if self.selected_row == row_idx and self.selected_col == col_idx and col != "Score":
                    pygame.draw.rect(self.screen, (100, 200, 255), rect)
                
                pygame.draw.rect(self.screen, jeopardy_dark_blue, rect, 1)

                text = self.font.render(cell_value[:20] + "..." if len(cell_value) > 20 else cell_value, True, text_color)
                self.screen.blit(text, (rect.x + 5, rect.y + 5))

    def draw_categories_table(self):
        if "Categories" not in self.data.columns:
            return

        # Merged header row
        merged_rect = pygame.Rect(0, 0, self.cell_width * 6, self.cell_height)
        pygame.draw.rect(self.screen, jeopardy_dark_blue, merged_rect)
        pygame.draw.rect(self.screen, jeopardy_gold, merged_rect, 2)
        text = self.font.render("CATEGORIES", True, white)
        text_rect = text.get_rect(center=merged_rect.center)
        self.screen.blit(text, text_rect)

        # Category row
        for i in range(6):
            cat_val = ""
            if i < len(self.data):
                cat_val = str(self.data.iloc[i].get("Categories", ""))

            cat_rect = pygame.Rect(i * self.cell_width, self.cell_height, self.cell_width, self.cell_height)
            pygame.draw.rect(self.screen, jeopardy_yellow, cat_rect)
            border_color = jeopardy_gold if self.editing_category_col == i else jeopardy_dark_blue
            pygame.draw.rect(self.screen, border_color, cat_rect, 2)
            
            text = self.font.render(cat_val[:18] + "..." if len(cat_val) > 18 else cat_val, True, black)
            self.screen.blit(text, (cat_rect.x + 5, cat_rect.y + 5))

    def draw_edit_box(self):
        if self.selected_row is not None or self.editing_category_col is not None:
            edit_rect = pygame.Rect(50, HEIGHT - 100, WIDTH - 100, 50)
            pygame.draw.rect(self.screen, white, edit_rect)
            pygame.draw.rect(self.screen, blue, edit_rect, 2)

            # Filter out null characters and ensure string type
            display_text = str(self.edit_text).replace('\x00', '')
            
            # Draw text
            text_surface = self.font.render(display_text, True, black)
            self.screen.blit(text_surface, (edit_rect.x + 10, edit_rect.y + 15))
            
            # Draw selection highlight if any
            if self.selection_start is not None and self.selection_end is not None:
                start = min(self.selection_start, self.selection_end)
                end = max(self.selection_start, self.selection_end)
                if start != end:
                    # Calculate positions
                    prefix = display_text[:start]
                    selected = display_text[start:end]
                    
                    prefix_width = self.font.size(prefix)[0]
                    selected_width = self.font.size(selected)[0]
                    
                    # Draw selection highlight
                    highlight_rect = pygame.Rect(
                        edit_rect.x + 10 + prefix_width,
                        edit_rect.y + 15,
                        selected_width,
                        self.font.get_height()
                    )
                    pygame.draw.rect(self.screen, (173, 216, 230), highlight_rect)  # Light blue
                    
                    # Redraw selected text over the highlight
                    selected_surface = self.font.render(selected, True, black)
                    self.screen.blit(selected_surface, (highlight_rect.x, highlight_rect.y))
            
            # Draw cursor if active
            if self.cursor_visible:
                cursor_x = edit_rect.x + 10 + self.font.size(display_text[:self.cursor_pos])[0]
                pygame.draw.line(self.screen, black, (cursor_x, edit_rect.y + 15), 
                            (cursor_x, edit_rect.y + 35), 2)
    def handle_text_selection(self, event):
        """Helper method to handle text selection logic"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Start new selection
            edit_box = pygame.Rect(50, HEIGHT - 100, WIDTH - 100, 50)
            if edit_box.collidepoint(event.pos):
                rel_x = event.pos[0] - edit_box.x - 10
                new_pos = self.get_cursor_position(self.edit_text, rel_x)
                
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    # Extend existing selection
                    if self.selection_start is None:
                        self.selection_start = self.cursor_pos
                    self.selection_end = new_pos
                else:
                    # Start new selection
                    self.selection_start = self.selection_end = new_pos
                    self.selection_anchor = new_pos
                
                self.cursor_pos = new_pos
                self.cursor_visible = True
                self.cursor_blink_time = pygame.time.get_ticks()
                return True
        
        elif event.type == pygame.MOUSEMOTION and event.buttons[0] == 1:
            # Drag to extend selection
            edit_box = pygame.Rect(50, HEIGHT - 100, WIDTH - 100, 50)
            if edit_box.collidepoint(event.pos):
                rel_x = event.pos[0] - edit_box.x - 10
                new_pos = self.get_cursor_position(self.edit_text, rel_x)
                
                if self.selection_anchor is not None:
                    self.selection_start = min(self.selection_anchor, new_pos)
                    self.selection_end = max(self.selection_anchor, new_pos)
                    self.cursor_pos = new_pos
                    self.cursor_visible = True
                    self.cursor_blink_time = pygame.time.get_ticks()
                return True
        
        return False
    def handle_events(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.cursor_blink_time > 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_blink_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                edit_box = pygame.Rect(50, HEIGHT - 100, WIDTH - 100, 50)
                
                if hasattr(self, 'last_click_time') and current_time - self.last_click_time < 300:
                    if edit_box.collidepoint(x, y) and (self.selected_row is not None or self.editing_category_col is not None):
                        rel_x = x - edit_box.x - 10
                        click_pos = self.get_cursor_position(self.edit_text, rel_x)
                        
                        text = self.edit_text
                        start = click_pos
                        end = click_pos
                        
                        while start > 0 and (text[start-1].isalnum() or text[start-1] in ("_", "-")):
                            start -= 1
                            
                        while end < len(text) and (text[end].isalnum() or text[end] in ("_", "-")):
                            end += 1
                            
                        if start != end:
                            self.selection_start = start
                            self.selection_end = end
                            self.selection_anchor = start
                            self.cursor_pos = end
                            self.cursor_visible = True
                            self.cursor_blink_time = current_time
                    continue
                
                self.last_click_time = current_time
                
                if edit_box.collidepoint(x, y):
                    rel_x = x - edit_box.x - 10
                    new_pos = self.get_cursor_position(self.edit_text, rel_x)
                    
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        if self.selection_start is None:
                            self.selection_start = self.cursor_pos
                        self.selection_end = new_pos
                    else:
                        self.selection_start = self.selection_end = new_pos
                        self.selection_anchor = new_pos
                    
                    self.cursor_pos = new_pos
                    self.cursor_visible = True
                    self.cursor_blink_time = current_time
                    continue

                if self.cell_height <= y < 2 * self.cell_height:
                    col = x // self.cell_width
                    if 0 <= col < 6 and col < len(self.data):
                        if self.editing_category_col != col:
                            if self.editing_category_col is not None:
                                self.data.at[self.editing_category_col, "Categories"] = self.edit_text
                            
                            self.editing_category_col = col
                            self.selected_row = None
                            self.selected_col = None
                            self.edit_text = str(self.data.iloc[col].get("Categories", ""))
                            self.cursor_pos = len(self.edit_text)
                            self.selection_start = self.selection_end = None
                            self.selection_anchor = None

                else:
                    headers = ["Row", "Col", "Question", "Answer", "Score"]
                    stretched_cell_width = WIDTH // len(headers)
                    col = x // stretched_cell_width
                    row = (y + self.scroll_offset - (4 * self.cell_height + 10)) // self.cell_height
                    
                    if 0 <= row < len(self.data) and 0 <= col < 5 and col != 4:
                        if self.selected_row != row or self.selected_col != col:
                            if self.selected_row is not None:
                                col_name = headers[self.selected_col]
                                if col_name in ["Row", "Col"]:
                                    try:
                                        self.data.at[self.selected_row, col_name] = int(self.edit_text)
                                    except ValueError:
                                        self.data.at[self.selected_row, col_name] = 1 if col_name == "Row" else 0
                                else:
                                    self.data.at[self.selected_row, col_name] = self.edit_text
                            
                            self.selected_row = row
                            self.selected_col = col
                            self.editing_category_col = None
                            col_name = headers[col]
                            self.edit_text = str(self.data.iloc[row][col_name])
                            self.cursor_pos = len(self.edit_text)
                            self.selection_start = self.selection_end = None
                            self.selection_anchor = None

            elif event.type == pygame.MOUSEMOTION and event.buttons[0] == 1:
                edit_box = pygame.Rect(50, HEIGHT - 100, WIDTH - 100, 50)
                if edit_box.collidepoint(event.pos):
                    rel_x = event.pos[0] - edit_box.x - 10
                    new_pos = self.get_cursor_position(self.edit_text, rel_x)
                    
                    if self.selection_anchor is not None:
                        self.selection_start = min(self.selection_anchor, new_pos)
                        self.selection_end = max(self.selection_anchor, new_pos)
                        self.cursor_pos = new_pos
                        self.cursor_visible = True
                        self.cursor_blink_time = current_time

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.selection_anchor = None

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in (4, 5):
                    if event.button == 4:
                        self.scroll_offset = max(0, self.scroll_offset - 20)
                    else:
                        self.scroll_offset += 20

            elif event.type == pygame.KEYDOWN:
                current_text = self.edit_text
                
                if self.selected_row is not None or self.editing_category_col is not None:
                    if event.key == pygame.K_RETURN:
                        if self.selected_row is not None:
                            col_name = ["Row", "Col", "Question", "Answer"][self.selected_col]
                            if col_name in ["Row", "Col"]:
                                try:
                                    self.data.at[self.selected_row, col_name] = int(self.edit_text)
                                except ValueError:
                                    self.data.at[self.selected_row, col_name] = 1 if col_name == "Row" else 0
                            else:
                                self.data.at[self.selected_row, col_name] = self.edit_text
                        elif self.editing_category_col is not None:
                            self.data.at[self.editing_category_col, "Categories"] = self.edit_text
                        
                        self.selected_row = None
                        self.selected_col = None
                        self.editing_category_col = None
                        self.selection_start = self.selection_end = None
                        self.selection_anchor = None
                    
                    elif event.key == pygame.K_ESCAPE:
                        if self.selected_row is not None:
                            col_name = ["Row", "Col", "Question", "Answer"][self.selected_col]
                            self.edit_text = str(self.data.iloc[self.selected_row][col_name])
                        elif self.editing_category_col is not None:
                            self.edit_text = str(self.data.iloc[self.editing_category_col].get("Categories", ""))
                        self.selection_start = self.selection_end = None
                        self.selection_anchor = None
                    
                    elif event.key == pygame.K_c and (event.mod & pygame.KMOD_CTRL):
                        if self.selection_start is not None and self.selection_end is not None:
                            start = min(self.selection_start, self.selection_end)
                            end = max(self.selection_start, self.selection_end)
                            selected_text = current_text[start:end]
                            pygame.scrap.put(pygame.SCRAP_TEXT, selected_text.encode('utf-8'))
                        else:
                            pygame.scrap.put(pygame.SCRAP_TEXT, current_text.encode('utf-8'))
                    
                    elif event.key == pygame.K_x and (event.mod & pygame.KMOD_CTRL):
                        if self.selection_start is not None and self.selection_end is not None:
                            start = min(self.selection_start, self.selection_end)
                            end = max(self.selection_start, self.selection_end)
                            selected_text = current_text[start:end]
                            pygame.scrap.put(pygame.SCRAP_TEXT, selected_text.encode('utf-8'))
                            self.edit_text = current_text[:start] + current_text[end:]
                            self.cursor_pos = start
                        else:
                            pygame.scrap.put(pygame.SCRAP_TEXT, current_text.encode('utf-8'))
                            self.edit_text = ""
                            self.cursor_pos = 0
                        self.selection_start = self.selection_end = None
                        self.selection_anchor = None
                    
                    elif event.key == pygame.K_v and (event.mod & pygame.KMOD_CTRL):
                        try:
                            clipboard_text = pygame.scrap.get(pygame.SCRAP_TEXT).decode('utf-8').strip()
                            if self.selection_start is not None and self.selection_end is not None:
                                start = min(self.selection_start, self.selection_end)
                                end = max(self.selection_start, self.selection_end)
                                self.edit_text = current_text[:start] + clipboard_text + current_text[end:]
                                self.cursor_pos = start + len(clipboard_text)
                            else:
                                self.edit_text = current_text[:self.cursor_pos] + clipboard_text + current_text[self.cursor_pos:]
                                self.cursor_pos += len(clipboard_text)
                            self.selection_start = self.selection_end = None
                            self.selection_anchor = None
                        except:
                            pass
                    
                    elif event.key == pygame.K_a and (event.mod & pygame.KMOD_CTRL):
                        self.selection_start = 0
                        self.selection_end = len(current_text)
                        self.selection_anchor = 0
                        self.cursor_pos = len(current_text)
                    
                    elif event.key == pygame.K_LEFT:
                        if event.mod & pygame.KMOD_SHIFT:
                            if self.selection_start is None:
                                self.selection_start = self.cursor_pos
                            self.cursor_pos = max(0, self.cursor_pos - 1)
                            self.selection_end = self.cursor_pos
                        else:
                            self.cursor_pos = max(0, self.cursor_pos - 1)
                            self.selection_start = self.selection_end = None
                            self.selection_anchor = None
                    
                    elif event.key == pygame.K_RIGHT:
                        if event.mod & pygame.KMOD_SHIFT:
                            if self.selection_start is None:
                                self.selection_start = self.cursor_pos
                            self.cursor_pos = min(len(current_text), self.cursor_pos + 1)
                            self.selection_end = self.cursor_pos
                        else:
                            self.cursor_pos = min(len(current_text), self.cursor_pos + 1)
                            self.selection_start = self.selection_end = None
                            self.selection_anchor = None
                    
                    elif event.key == pygame.K_HOME:
                        if event.mod & pygame.KMOD_SHIFT:
                            if self.selection_start is None:
                                self.selection_start = self.cursor_pos
                            self.cursor_pos = 0
                            self.selection_end = 0
                        else:
                            self.cursor_pos = 0
                            self.selection_start = self.selection_end = None
                            self.selection_anchor = None
                    
                    elif event.key == pygame.K_END:
                        if event.mod & pygame.KMOD_SHIFT:
                            if self.selection_start is None:
                                self.selection_start = self.cursor_pos
                            self.cursor_pos = len(current_text)
                            self.selection_end = len(current_text)
                        else:
                            self.cursor_pos = len(current_text)
                            self.selection_start = self.selection_end = None
                            self.selection_anchor = None
                    
                    elif event.key == pygame.K_BACKSPACE:
                        if self.selection_start is not None and self.selection_end is not None:
                            start = min(self.selection_start, self.selection_end)
                            end = max(self.selection_start, self.selection_end)
                            self.edit_text = current_text[:start] + current_text[end:]
                            self.cursor_pos = start
                            self.selection_start = self.selection_end = None
                            self.selection_anchor = None
                        elif self.cursor_pos > 0:
                            self.edit_text = current_text[:self.cursor_pos-1] + current_text[self.cursor_pos:]
                            self.cursor_pos -= 1
                    
                    elif event.key == pygame.K_DELETE:
                        if self.selection_start is not None and self.selection_end is not None:
                            start = min(self.selection_start, self.selection_end)
                            end = max(self.selection_start, self.selection_end)
                            self.edit_text = current_text[:start] + current_text[end:]
                            self.cursor_pos = start
                            self.selection_start = self.selection_end = None
                            self.selection_anchor = None
                        elif self.cursor_pos < len(current_text):
                            self.edit_text = current_text[:self.cursor_pos] + current_text[self.cursor_pos+1:]
                    
                    elif event.unicode and event.unicode.isprintable():
                        if self.selection_start is not None and self.selection_end is not None:
                            start = min(self.selection_start, self.selection_end)
                            end = max(self.selection_start, self.selection_end)
                            self.edit_text = current_text[:start] + event.unicode + current_text[end:]
                            self.cursor_pos = start + 1
                        else:
                            self.edit_text = current_text[:self.cursor_pos] + event.unicode + current_text[self.cursor_pos:]
                            self.cursor_pos += 1
                        self.selection_start = self.selection_end = None
                        self.selection_anchor = None
                    
                    self.cursor_visible = True
                    self.cursor_blink_time = current_time

        return True
    def get_cursor_position(self, text, x_pos):
        """Determine cursor position based on x position in text"""
        if not text:
            return 0
        
        width = 0
        for i, char in enumerate(text):
            char_width = self.font.size(char)[0]
            if x_pos < width + char_width // 2:
                return i
            width += char_width
        
        return len(text)

    def show_popup(self, message, duration=2000):
        screen_copy = self.screen.copy()
        
        popup_rect = pygame.Rect(WIDTH // 4, HEIGHT // 3, WIDTH // 2, 100)
        pygame.draw.rect(self.screen, jeopardy_dark_blue, popup_rect)
        pygame.draw.rect(self.screen, jeopardy_gold, popup_rect, 3)

        text = self.font.render(message, True, white)
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

            # Save button
            save_btn = pygame.Rect(WIDTH//2 - 100, HEIGHT - 60, 200, 50)
            pygame.draw.rect(self.screen, jeopardy_blue, save_btn)
            pygame.draw.rect(self.screen, jeopardy_gold, save_btn, 3)
            save_text = self.font.render("SAVE & EXIT", True, white)
            
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()
            if save_btn.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, jeopardy_dark_blue, save_btn)
                pygame.draw.rect(self.screen, jeopardy_yellow, save_btn, 3)
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