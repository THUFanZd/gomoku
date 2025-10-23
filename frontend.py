import pygame
from macro import *

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

