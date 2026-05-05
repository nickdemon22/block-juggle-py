import pygame
import math
from settings import *

class Shape:
    def __init__(self, matrix, texture, start_pos):
        self.matrix = matrix
        self.texture = texture
        self.start_pos = start_pos  
        self.x, self.y = start_pos
        self.target_x, self.target_y = start_pos 
        self.is_dragging = False
        
        self.scale = 0.0          
        self.target_scale = 0.6   

    def update(self):
        if not self.is_dragging:
            self.x += (self.target_x - self.x) * 0.25
            self.y += (self.target_y - self.y) * 0.25
            self.scale += (self.target_scale - self.scale) * 0.15
        else:
            self.scale += (1.0 - self.scale) * 0.25

    def draw(self, surface):
        if self.scale < 0.05: 
            return

        # Точный расчет размера без дробных потерь
        cell_size = CELL_SIZE * self.scale
        draw_size = math.ceil(cell_size) 
        
        scaled_texture = pygame.transform.scale(self.texture, (draw_size, draw_size))

        shadow_surf = pygame.Surface((draw_size, draw_size), pygame.SRCALPHA)
        shadow_surf.fill((0, 0, 0, int(80 * self.scale))) 

        # 1. СНАЧАЛА рисуем ВСЕ тени (чтобы они не ложились поверх соседних блоков)
        for r, row in enumerate(self.matrix):
            for c, val in enumerate(row):
                if val:
                    px = self.x + int(c * cell_size)
                    py = self.y + int(r * cell_size)
                    surface.blit(shadow_surf, (px + int(5 * self.scale), py + int(5 * self.scale)))

        # 2. ЗАТЕМ рисуем ВСЕ текстуры (поверх теней)
        for r, row in enumerate(self.matrix):
            for c, val in enumerate(row):
                if val:
                    px = self.x + int(c * cell_size)
                    py = self.y + int(r * cell_size)
                    surface.blit(scaled_texture, (px, py))

    def get_rect(self):
        cell_size = CELL_SIZE * self.scale
        width = len(self.matrix[0]) * cell_size
        height = len(self.matrix) * cell_size
        return pygame.Rect(self.x, self.y, width, height)

    def snap_to_grid(self, board):
        grid_x = round((self.x - GRID_OFFSET_X) / CELL_SIZE)
        grid_y = round((self.y - GRID_OFFSET_Y) / CELL_SIZE)

        if board.can_place(self.matrix, grid_x, grid_y):
            board.place(self.matrix, self.texture, grid_x, grid_y)
            return True
        else:
            self.target_x, self.target_y = self.start_pos
            return False