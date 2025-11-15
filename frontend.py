import pygame
import numpy as np
from macro import *
from button import *   # 使用按钮对象（start_button 等）

pygame.init()

# 字体初始化
def init_font(size):
    """初始化字体，兼容macOS和Windows"""
    font_names = [
        'Arial Unicode MS',  # macOS
        'SimHei',  # Windows 黑体
        'Microsoft YaHei',  # Windows 微软雅黑
        'SimSun',  # Windows 宋体
        'PingFang SC',  # macOS
        'Helvetica',  # 通用
        'Arial'  # 通用
    ]

    for name in font_names:
        try:
            font = pygame.font.SysFont(name, size)
            test_surface = font.render("测试", True, BLACK)
            if test_surface.get_width() > 0:
                return font
        except:
            continue

    return pygame.font.Font(None, size)

# 初始化不同大小的字体
font_small = init_font(24)
font_medium = init_font(36)
font_large = init_font(72)
font_title = init_font(96)


def count_pieces(board, player_num: int):
    return int(np.sum(board == player_num))
