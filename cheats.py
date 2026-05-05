import pygame
import os
from settings import *

# Состояния
menu_open = False
endless_mode = False

def get_font(size):
    if os.path.exists("assets/my_font.ttf"):
        return pygame.font.Font("assets/my_font.ttf", size)
    return pygame.font.SysFont("Arial", size, bold=True)

# Хитбоксы элементов UI
btn_open = pygame.Rect(20, 80, 70, 35) # Кнопка открытия на главном экране
menu_rect = pygame.Rect(WIDTH//2 - 140, HEIGHT//2 - 180, 280, 360)

# Кнопки внутри меню
btn_score = pygame.Rect(menu_rect.x + 20, menu_rect.y + 60, 240, 45)
btn_clear = pygame.Rect(menu_rect.x + 20, menu_rect.y + 115, 240, 45)
btn_mini = pygame.Rect(menu_rect.x + 20, menu_rect.y + 170, 240, 45)
btn_endless = pygame.Rect(menu_rect.x + 20, menu_rect.y + 225, 240, 45)
btn_close = pygame.Rect(menu_rect.x + 20, menu_rect.y + 290, 240, 40)

def clear_board(board):
    """ Красиво очищает поле, отправляя блоки в анимацию схлопывания """
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if board.grid[r][c] != 0:
                board.animating_blocks.append({
                    'row': r, 'col': c, 
                    'tex': board.grid[r][c], 
                    'scale': 1.0
                })
                board.grid[r][c] = 0

def handle_event(event, board, active_shapes):
    """ Перехватывает клики для графического меню """
    global menu_open, endless_mode
    
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if not menu_open:
            if btn_open.collidepoint(event.pos):
                menu_open = True
                return True # Блокируем клик для остальной игры
        else:
            if btn_score.collidepoint(event.pos):
                board.score += 500
            elif btn_clear.collidepoint(event.pos):
                clear_board(board)
            elif btn_mini.collidepoint(event.pos):
                for shape in active_shapes:
                    shape.matrix = [[1]]
            elif btn_endless.collidepoint(event.pos):
                endless_mode = not endless_mode
            elif btn_close.collidepoint(event.pos):
                menu_open = False
            
            # Если меню открыто и мы кликнули внутри него, поглощаем клик
            if menu_rect.collidepoint(event.pos):
                return True
    return False

def check_endless(board, active_shapes):
    """ Спасает от проигрыша, автоматически очищая поле """
    global endless_mode
    if endless_mode:
        is_stuck = True
        for shape in active_shapes:
            for y in range(GRID_SIZE):
                for x in range(GRID_SIZE):
                    if board.can_place(shape.matrix, x, y):
                        is_stuck = False
                        break
                if not is_stuck: break
            if not is_stuck: break
            
        if is_stuck and active_shapes:
            clear_board(board) # Спасение! Поле взрывается, игра продолжается

def draw(screen):
    """ Отрисовка кнопки и самого меню """
    global endless_mode
    
    # Кнопка "Меню" на игровом экране
    pygame.draw.rect(screen, (80, 80, 100), btn_open, border_radius=8)
    txt = get_font(18).render("Меню", True, (255, 255, 255))
    screen.blit(txt, (btn_open.centerx - txt.get_width()//2, btn_open.centery - txt.get_height()//2))

    if menu_open:
        # Затемнение фона
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Основа меню
        pygame.draw.rect(screen, (40, 50, 60), menu_rect, border_radius=15)
        pygame.draw.rect(screen, (255, 215, 0), menu_rect, width=3, border_radius=15)

        title = get_font(28).render("Секретное Меню", True, (255, 215, 0))
        screen.blit(title, (menu_rect.centerx - title.get_width()//2, menu_rect.y + 15))

        # Функция для кнопок с эффектом наведения
        mouse_pos = pygame.mouse.get_pos()
        def draw_btn(rect, text, bg_color):
            color = (min(bg_color[0]+30, 255), min(bg_color[1]+30, 255), min(bg_color[2]+30, 255)) if rect.collidepoint(mouse_pos) else bg_color
            pygame.draw.rect(screen, color, rect, border_radius=10)
            txt_surf = get_font(20).render(text, True, (255, 255, 255))
            screen.blit(txt_surf, (rect.centerx - txt_surf.get_width()//2, rect.centery - txt_surf.get_height()//2))

        draw_btn(btn_score, "+500 Очков", (200, 100, 50))
        draw_btn(btn_clear, "Очистить поле (Спасение)", (200, 50, 50))
        draw_btn(btn_mini, "Сделать фигуры 1x1", (50, 150, 200))
        
        endless_col = (50, 180, 50) if endless_mode else (120, 120, 120)
        draw_btn(btn_endless, f"Бесконечно: {'ВКЛ' if endless_mode else 'ВЫКЛ'}", endless_col)
        
        draw_btn(btn_close, "Закрыть меню", (100, 100, 100))