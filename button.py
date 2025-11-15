import pygame
from macro import *

# 按钮定义
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False

    def draw(self, surface, font):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=8)  # 边框

        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
# 创建按钮
start_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 60, "START", GREEN, (100, 200, 100))
title_exit_button = Button(WIDTH//2 - 100, HEIGHT//2 + 130, 200, 60, "EXIT GAME", RED, (255, 100, 100))
pvp_button = Button(WIDTH // 2 - 150, HEIGHT // 2, 300, 60, "Player vs Player", BLUE, (100, 100, 255))
pvc_button = Button(WIDTH // 2 - 150, HEIGHT // 2 + 80, 300, 60, "Player vs Computer", GREEN, (100, 200, 100))
back_button = Button(20, HEIGHT - 70, 100, 40, "Back", RED, (255, 100, 100))
undo_button = Button(WIDTH - 245, 5, 100, 40, "Undo", BLUE, (100, 100, 255))
restart_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 50, "Restart", WHITE, GRAY, BLACK)
exit_button = Button(WIDTH - 120, 5, 100, 40, "EXIT", RED, (255, 100, 100))
send_button = Button(WIDTH // 2 + 50, HEIGHT // 2 + 50, 100, 40, "Send", GREEN, (100, 200, 100))
# 人人对战：对手悔棋请求确认对话框按钮
undo_accept_button = Button(WIDTH // 2 - 140, HEIGHT // 2 + 30, 120, 40, "Yes", GREEN, (100, 200, 100))
undo_reject_button = Button(WIDTH // 2 + 20,  HEIGHT // 2 + 30, 120, 40, "No",  RED,   (255, 100, 100))
# 难度选择按钮
easy_button = Button(WIDTH // 2 - 150, HEIGHT // 2 - 60, 300, 60, "Easy", GREEN, (100, 200, 100))
medium_button = Button(WIDTH // 2 - 150, HEIGHT // 2 + 20, 300, 60, "Medium", BLUE, (100, 100, 255))
hard_button = Button(WIDTH // 2 - 150, HEIGHT // 2 + 100, 300, 60, "Hard", RED, (255, 100, 100))
difficulty_back_button = Button(20, HEIGHT - 70, 100, 40, "Back", RED, (255, 100, 100))
# 执棋颜色选择按钮（仅人机模式）
choose_black_button = Button(WIDTH // 2 - 150, HEIGHT // 2 - 20, 300, 60, "Play as Black", BLUE, (100, 100, 255))
choose_white_button = Button(WIDTH // 2 - 150, HEIGHT // 2 + 60, 300, 60, "Play as White", GREEN, (100, 200, 100))
side_back_button   = Button(20, HEIGHT - 70, 100, 40, "Back", RED, (255, 100, 100))