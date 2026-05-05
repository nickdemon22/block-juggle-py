import pygame
import random
import sys
import os
from settings import *
from board import Board
from shape import Shape

import cheats

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Block Juggle")
clock = pygame.time.Clock()

# --- ЗАГРУЗКА СВОЕГО ШРИФТА ---
def load_custom_font(filename, size):
    if os.path.exists(filename):
        # Загружаем твой .ttf файл
        return pygame.font.Font(filename, size)
    else:
        # Если файла нет, используем стандартный системный
        return pygame.font.SysFont("Arial", size, bold=True)

# Теперь используем нашу функцию (положи my_font.ttf в папку assets)
font_score = load_custom_font("assets/my_font.ttf", 56)
font_best = load_custom_font("assets/my_font.ttf", 28)
font_go_title = load_custom_font("assets/my_font.ttf", 60)
font_go_label = load_custom_font("assets/my_font.ttf", 22)
font_go_big_score = load_custom_font("assets/my_font.ttf", 64)

# Цвета для Game Over
COLOR_LABEL = (140, 200, 210)
COLOR_SCORE = (255, 255, 255)
COLOR_BEST = (245, 150, 30)

# Загрузка текстур блоков
TEXTURE_FILES = {
    "assets/block_red.png": (220, 50, 50),
    "assets/block_blue.png": (50, 50, 220),
    "assets/block_green.png": (50, 220, 50),
    "assets/block_purple.png": (150, 50, 220),
    "assets/block_orange.png": (240, 140, 30),
    "assets/block_cyan.png": (50, 200, 220)
}

def load_block_image(filename, fallback_color):
    if os.path.exists(filename):
        img = pygame.image.load(filename).convert_alpha()
        return pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
    else:
        surf = pygame.Surface((CELL_SIZE, CELL_SIZE))
        surf.fill(fallback_color)
        pygame.draw.rect(surf, (255, 255, 255), (0, 0, CELL_SIZE, CELL_SIZE), 2)
        return surf

TEXTURES = []
for filename, color in TEXTURE_FILES.items():
    TEXTURES.append(load_block_image(filename, color))

def load_background(filename):
    if os.path.exists(filename):
        img = pygame.image.load(filename).convert()
        return pygame.transform.scale(img, (WIDTH, HEIGHT))
    return None

bg_image = load_background("assets/bg.png")

def load_icon(filename, size):
    if os.path.exists(filename):
        img = pygame.image.load(filename).convert_alpha()
        return pygame.transform.scale(img, size)
    return None

crown_icon = load_icon("assets/crown.png", (32, 32))

# Кнопка Play (для экрана Game Over)
play_btn_size = (260, 75)
play_btn_rect = pygame.Rect(WIDTH // 2 - play_btn_size[0] // 2, HEIGHT - 200, play_btn_size[0], play_btn_size[1])

def load_play_button():
    if os.path.exists("assets/play_button.png"):
        img = pygame.image.load("assets/play_button.png").convert_alpha()
        return pygame.transform.scale(img, play_btn_size)
    else:
        surf = pygame.Surface(play_btn_size, pygame.SRCALPHA)
        pygame.draw.rect(surf, (60, 200, 60), (0, 0, *play_btn_size), border_radius=25)
        pygame.draw.polygon(surf, (255, 255, 255), [(115, 22), (115, 52), (145, 37)])
        return surf

play_btn_img = load_play_button()

# --- КНОПКА РЕСТАРТА (для главного экрана) ---
restart_btn_size = (44, 44)
# Позиция: правый верхний угол (отступаем от ширины экрана)
restart_btn_rect = pygame.Rect(WIDTH - restart_btn_size[0] - 20, 20, restart_btn_size[0], restart_btn_size[1])

def load_restart_button():
    if os.path.exists("assets/restart.png"):
        img = pygame.image.load("assets/restart.png").convert_alpha()
        return pygame.transform.scale(img, restart_btn_size)
    else:
        # Заглушка, если нет картинки: красный кружок
        surf = pygame.Surface(restart_btn_size, pygame.SRCALPHA)
        pygame.draw.circle(surf, (220, 80, 80), (restart_btn_size[0]//2, restart_btn_size[1]//2), restart_btn_size[0]//2)
        # Белый квадрат внутри (символ стоп/рестарт)
        pygame.draw.rect(surf, (255, 255, 255), (14, 14, 16, 16))
        return surf

restart_btn_img = load_restart_button()
# ----------------------------------------------

def get_high_score():
    if os.path.exists("highscore.txt"):
        with open("highscore.txt", "r") as f:
            try:
                return int(f.read())
            except ValueError:
                return 0
    return 0

def save_high_score(score):
    with open("highscore.txt", "w") as f:
        f.write(str(score))

def spawn_shapes():
    shapes = []
    positions = [(50, 650), (200, 650), (350, 650)]
    for pos in positions:
        matrix = random.choice(SHAPES_DATA)
        texture = random.choice(TEXTURES)
        shapes.append(Shape(matrix, texture, pos))
    return shapes

def check_game_over(board, shapes):
    if not shapes:
        return False
    for shape in shapes:
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if board.can_place(shape.matrix, x, y):
                    return False
    return True

# ... (весь код загрузки шрифтов, картинок и т.д. сверху оставляем без изменений) ...

def main():
    board = Board()
    active_shapes = spawn_shapes()
    dragged_shape = None
    game_over = False
    best_score = get_high_score()
    
    # Переменная для контроля анимации проигрыша (от 0.0 до 1.0)
    go_anim_progress = 0.0

    while True:
        if bg_image:
            screen.blit(bg_image, (0, 0))
        else:
            screen.fill(BG_COLOR)

        if not game_over:
            board.update()
            for shape in active_shapes:
                shape.update()
        else:
            # Двигаем анимацию Game Over вперед (0.04 = скорость появления)
            if go_anim_progress < 1.0:
                go_anim_progress += 0.04
                if go_anim_progress > 1.0:
                    go_anim_progress = 1.0

        for event in pygame.event.get():

            if not game_over:
                if cheats.handle_event(event, board, active_shapes):
                    continue # Пропускаем остальные действия, если кликнули по меню
                    cheats.check_endless(board, active_shapes)
            if event.type == pygame.QUIT:
                if board.score > best_score:
                    save_high_score(board.score)
                pygame.quit()
                sys.exit()

            if not game_over:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_pos = event.pos
                        
                        if restart_btn_rect.collidepoint(mouse_pos):
                            if board.score > best_score:
                                best_score = board.score
                                save_high_score(best_score)
                            
                            board = Board()
                            active_shapes = spawn_shapes()
                            dragged_shape = None
                            continue 

                        for shape in active_shapes:
                            if shape.get_rect().collidepoint(mouse_pos):
                                dragged_shape = shape
                                dragged_shape.is_dragging = True
                                dragged_shape.x = mouse_pos[0] - (CELL_SIZE * shape.scale) // 2
                                dragged_shape.y = mouse_pos[1] - (CELL_SIZE * shape.scale) // 2
                                break

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and dragged_shape:
                        dragged_shape.is_dragging = False
                        if dragged_shape.snap_to_grid(board):
                            active_shapes.remove(dragged_shape)
                            if board.score > best_score:
                                best_score = board.score
                                save_high_score(best_score)
                                
                            if not active_shapes:
                                active_shapes = spawn_shapes()
                        dragged_shape = None

                elif event.type == pygame.MOUSEMOTION:
                    if dragged_shape and dragged_shape.is_dragging:
                        dragged_shape.x += event.rel[0]
                        dragged_shape.y += event.rel[1]

            else:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        # Разрешаем кликнуть только когда анимация выезда закончилась
                        if play_btn_rect.collidepoint(event.pos) and go_anim_progress >= 1.0:
                            board = Board()
                            active_shapes = spawn_shapes()
                            dragged_shape = None
                            game_over = False
                            go_anim_progress = 0.0 # Сбрасываем для следующего раза

        # Проверка на проигрыш
        if not game_over and check_game_over(board, active_shapes):
            game_over = True
            go_anim_progress = 0.0 # Запускаем анимацию
            if board.score > best_score:
                save_high_score(board.score)

        # Отрисовка игры (рисуется ВСЕГДА, чтобы быть на фоне под экраном Game Over)
        board.draw(screen)

        for shape in active_shapes:
            if shape != dragged_shape:
                shape.draw(screen)

        if dragged_shape:
            dragged_shape.draw(screen)

        score_text = font_score.render(str(board.score), True, TEXT_COLOR)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 70))

        best_str = str(best_score)
        if crown_icon:
            screen.blit(crown_icon, (20, 20))
            best_text = font_best.render(best_str, True, (255, 215, 0))
            screen.blit(best_text, (60, 22))
        else:
            best_text = font_best.render(f"Best: {best_str}", True, (255, 215, 0))
            screen.blit(best_text, (20, 20))
            
        screen.blit(restart_btn_img, restart_btn_rect.topleft)

        # === НОВАЯ ОТРИСОВКА GAME OVER С АНИМАЦИЕЙ ===
        if game_over:
            # Математика плавности (кубическое замедление)
            ease_t = 1 - (1 - go_anim_progress) ** 3
            alpha_val = int(255 * ease_t)
            slide_y = int(-50 * (1 - ease_t)) # Текст выезжает сверху на 50 пикселей

            # Полупрозрачный черный фон
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, int(180 * ease_t)))
            screen.blit(overlay, (0, 0))

            # Game Over Title
            go_title = font_go_title.render("Game Over", True, COLOR_LABEL)
            go_title.set_alpha(alpha_val)
            screen.blit(go_title, (WIDTH // 2 - go_title.get_width() // 2, 140 + slide_y))

            # Score Label
            score_label = font_go_label.render("Score", True, COLOR_LABEL)
            score_label.set_alpha(alpha_val)
            screen.blit(score_label, (WIDTH // 2 - score_label.get_width() // 2, 280 + slide_y))

            # Score Value
            score_val = font_go_big_score.render(str(board.score), True, COLOR_SCORE)
            score_val.set_alpha(alpha_val)
            screen.blit(score_val, (WIDTH // 2 - score_val.get_width() // 2, 320 + slide_y))

            # Best Score Label
            best_label = font_go_label.render("Best score", True, COLOR_LABEL)
            best_label.set_alpha(alpha_val)
            screen.blit(best_label, (WIDTH // 2 - best_label.get_width() // 2, 440 + slide_y))

            # Best Score Value
            best_val = font_go_big_score.render(str(best_score), True, COLOR_BEST)
            best_val.set_alpha(alpha_val)
            screen.blit(best_val, (WIDTH // 2 - best_val.get_width() // 2, 480 + slide_y))

            # Play Button
            play_btn_copy = play_btn_img.copy()
            play_btn_copy.set_alpha(alpha_val)
            screen.blit(play_btn_copy, (play_btn_rect.x, play_btn_rect.y + slide_y))

        #cheats.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()