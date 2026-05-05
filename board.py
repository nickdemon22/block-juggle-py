import pygame
from settings import *

class Board:
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.score = 0
        self.animating_blocks = [] # Список для "умирающих" блоков

    def update(self):
        # Уменьшаем размер удаляемых блоков каждый кадр
        for b in self.animating_blocks[:]:
            b['scale'] -= 0.1 # Скорость исчезновения (за 10 кадров)
            if b['scale'] <= 0:
                self.animating_blocks.remove(b)

    def draw(self, surface):
        # 1. Сетка
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = GRID_OFFSET_X + col * CELL_SIZE
                y = GRID_OFFSET_Y + row * CELL_SIZE
                pygame.draw.rect(surface, GRID_COLOR, (x, y, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(surface, LINE_COLOR, (x, y, CELL_SIZE, CELL_SIZE), 1)
        
        # 2. Обычные статические блоки
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col] != 0:
                    x = GRID_OFFSET_X + col * CELL_SIZE
                    y = GRID_OFFSET_Y + row * CELL_SIZE
                    surface.blit(self.grid[row][col], (x, y))

        # 3. Анимация удаляемых блоков (они рисуются поверх всего)
        for b in self.animating_blocks:
            size = int(CELL_SIZE * b['scale'])
            if size > 0:
                scaled_tex = pygame.transform.scale(b['tex'], (size, size))
                # Центрируем уменьшенный блок в ячейке
                offset = (CELL_SIZE - size) // 2
                x = GRID_OFFSET_X + b['col'] * CELL_SIZE + offset
                y = GRID_OFFSET_Y + b['row'] * CELL_SIZE + offset
                surface.blit(scaled_tex, (x, y))

    def can_place(self, shape_matrix, grid_x, grid_y):
        for r, row in enumerate(shape_matrix):
            for c, val in enumerate(row):
                if val:
                    if (grid_y + r >= GRID_SIZE or grid_x + c >= GRID_SIZE or 
                        grid_y + r < 0 or grid_x + c < 0 or 
                        self.grid[grid_y + r][grid_x + c] != 0):
                        return False
        return True

    def place(self, shape_matrix, texture, grid_x, grid_y):
        blocks_placed = 0
        for r, row in enumerate(shape_matrix):
            for c, val in enumerate(row):
                if val:
                    self.grid[grid_y + r][grid_x + c] = texture
                    blocks_placed += 1
        self.score += blocks_placed
        self.check_lines()

    def check_lines(self):
        lines_to_clear_rows = []
        lines_to_clear_cols = []

        for row in range(GRID_SIZE):
            if all(self.grid[row][col] != 0 for col in range(GRID_SIZE)):
                lines_to_clear_rows.append(row)

        for col in range(GRID_SIZE):
            if all(self.grid[row][col] != 0 for row in range(GRID_SIZE)):
                lines_to_clear_cols.append(col)

        # Собираем уникальные ячейки для удаления (чтобы блок на пересечении не удалился дважды)
        cleared_cells = set()
        for row in lines_to_clear_rows:
            for col in range(GRID_SIZE):
                cleared_cells.add((row, col))
        for col in lines_to_clear_cols:
            for row in range(GRID_SIZE):
                cleared_cells.add((row, col))

        # Переносим блоки в список анимации и очищаем ячейки
        for r, c in cleared_cells:
            if self.grid[r][c] != 0:
                self.animating_blocks.append({
                    'row': r, 'col': c, 
                    'tex': self.grid[r][c], 
                    'scale': 1.0 # Начальный масштаб перед исчезновением
                })
                self.grid[r][c] = 0

        self.score += len(lines_to_clear_rows) * 10 
        self.score += len(lines_to_clear_cols) * 10