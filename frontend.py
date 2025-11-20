import pygame
import numpy as np
from macro import *
from button import *   # 使用按钮对象（start_button 等）

pygame.font.init()  # 新增这一行，确保可以创建字体

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

# 房间号输入界面
def draw_room_number_input(
    screen,
    room_waiting,
    room_input_active,
    room_input_rect,
    room_input_text,
    room_hint_color,
    room_border_color_idle,
    room_border_color_active,
):
    screen.fill(BROWN)

    title_text = font_large.render("Enter Room Number", True, BLACK)
    screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4)))

    if not room_waiting:
        border_color = room_border_color_active if room_input_active else room_border_color_idle
        pygame.draw.rect(screen, WHITE, room_input_rect)
        pygame.draw.rect(screen, border_color, room_input_rect, 2)

        if room_input_text:
            text_surf = font_medium.render(room_input_text, True, BLACK)
        else:
            text_surf = font_medium.render("Type digits and press Enter", True, room_hint_color)
        text_rect = text_surf.get_rect(midleft=(room_input_rect.x + 10, room_input_rect.centery))
        screen.blit(text_surf, text_rect)

        send_button.draw(screen, font_medium)
        back_button.draw(screen, font_small)
    else:
        wait_text = font_large.render("Waiting...", True, BLACK)
        screen.blit(wait_text, wait_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10)))
        back_button.draw(screen, font_small)

# 标题界面
def draw_title_screen(screen):
    screen.fill(BROWN)

    title_text = font_title.render("Gomoku Game", True, BLACK)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(title_text, title_rect)

    start_button.draw(screen, font_medium)
    title_exit_button.draw(screen, font_medium)

    hint_text = font_small.render("Click to start or exit.", True, BLACK)
    hint_rect = hint_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 300))
    screen.blit(hint_text, hint_rect)

# 模式选择界面
def draw_mode_select(screen):
    screen.fill(BROWN)

    title_text = font_large.render("Mode", True, BLACK)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    screen.blit(title_text, title_rect)

    pvp_button.draw(screen, font_medium)
    pvc_button.draw(screen, font_medium)
    back_button.draw(screen, font_small)

    desc_text = font_small.render("Player vs Player: Two players take turns", True, BLACK)
    desc_rect = desc_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 300))
    screen.blit(desc_text, desc_rect)

    desc_text2 = font_small.render("Player vs Computer: Play against AI", True, BLACK)
    desc_rect2 = desc_text2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 330))
    screen.blit(desc_text2, desc_rect2)

# 难度选择界面
def draw_difficulty_select(screen, easy_button, medium_button, hard_button, difficulty_back_button):
    screen.fill(BROWN)

    title_text = font_large.render("Select Difficulty", True, BLACK)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    screen.blit(title_text, title_rect)

    easy_button.draw(screen, font_medium)
    medium_button.draw(screen, font_medium)
    hard_button.draw(screen, font_medium)

    difficulty_back_button.draw(screen, font_small)

    desc_text = font_small.render("Easy: AI makes quick moves", True, BLACK)
    desc_rect = desc_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 180))
    screen.blit(desc_text, desc_rect)

    desc_text2 = font_small.render("Medium: Balanced AI", True, BLACK)
    desc_rect2 = desc_text2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 210))
    screen.blit(desc_text2, desc_rect2)

    desc_text3 = font_small.render("Hard: Challenging AI", True, BLACK)
    desc_rect3 = desc_text3.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 240))
    screen.blit(desc_text3, desc_rect3)

# 选择执棋颜色界面
def draw_side_select(screen, choose_black_button, choose_white_button, side_back_button):
    screen.fill(BROWN)

    title_text = font_large.render("Choose Side", True, BLACK)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    screen.blit(title_text, title_rect)

    choose_black_button.draw(screen, font_medium)
    choose_white_button.draw(screen, font_medium)
    side_back_button.draw(screen, font_small)

    tip_text = font_small.render("Black moves first", True, BLACK)
    tip_rect = tip_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 150))
    screen.blit(tip_text, tip_rect)

# 棋盘
def draw_board(screen):
    screen.fill(BROWN)

    for i in range(LINE_COUNT):
        pygame.draw.line(
            screen, BLACK,
            (GRID_SIZE, GRID_SIZE * (i + 1)),
            (WIDTH - GRID_SIZE, GRID_SIZE * (i + 1)),
            2
        )
        pygame.draw.line(
            screen, BLACK,
            (GRID_SIZE * (i + 1), GRID_SIZE),
            (GRID_SIZE * (i + 1), HEIGHT - GRID_SIZE),
            2
        )

    points = [(3, 3), (3, 11), (7, 7), (11, 3), (11, 11)]
    for x, y in points:
        pygame.draw.circle(
            screen, BLACK,
            (GRID_SIZE * (x + 1), GRID_SIZE * (y + 1)),
            5
        )

# 棋子
def draw_pieces(screen, board):
    for i in range(LINE_COUNT):
        for j in range(LINE_COUNT):
            if board[i][j] == 1:
                pygame.draw.circle(
                    screen, BLACK,
                    (GRID_SIZE * (j + 1), GRID_SIZE * (i + 1)),
                    GRID_SIZE // 2 - 2
                )
            elif board[i][j] == 2:
                pygame.draw.circle(
                    screen, WHITE,
                    (GRID_SIZE * (j + 1), GRID_SIZE * (i + 1)),
                    GRID_SIZE // 2 - 2
                )

# 游戏信息显示
def draw_game_info(
    screen,
    board,
    current_player,
    game_over,
    winner,
    game_mode,
    ai_difficulty,
    human_color,
    ai_color,
    undo_request_pending,
    move_history,
):
    if not game_over:
        if current_player == 1:
            player_text = font_small.render("Current: Black", True, BLACK)
        else:
            player_text = font_small.render("Current: White", True, BLACK)
    else:
        if winner == 1:
            player_text = font_small.render("Game Over: Black Wins!", True, RED)
        else:
            player_text = font_small.render("Game Over: White Wins!", True, RED)
    screen.blit(player_text, (10, 10))

    black_count = count_pieces(board, 1)
    white_count = count_pieces(board, 2)
    count_text = font_small.render(f"Black: {black_count}  White: {white_count}", True, BLACK)
    screen.blit(count_text, (10, 30))

    mode_text = font_small.render(
        f"Mode: {'Player vs Player' if game_mode == PVP_MODE else 'Player vs Computer'}",
        True,
        BLACK,
    )
    screen.blit(mode_text, (300, 10))

    if game_mode == PVC_MODE:
        difficulty_names = ["Easy", "Medium", "Hard"]
        difficulty_text = font_small.render(f"Difficulty: {difficulty_names[ai_difficulty]}", True, BLACK)
        screen.blit(difficulty_text, (300, 40))
        side_text = font_small.render(f"You: {'Black' if human_color == 1 else 'White'}", True, BLACK)
        screen.blit(side_text, (300, 60))

    if game_mode == PVP_MODE and undo_request_pending:
        status_text = font_small.render("Waiting for opponent to accept undo...", True, BLACK)
        screen.blit(status_text, (300, 40))

    if move_history and not game_over:
        undo_button.draw(screen, font_small)
    exit_button.draw(screen, font_small)

# 悔棋对话框
def draw_undo_dialog(screen):
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 150))
    screen.blit(s, (0, 0))

    box_w, box_h = 420, 180
    box_rect = pygame.Rect((WIDTH - box_w) // 2, (HEIGHT - box_h) // 2, box_w, box_h)
    pygame.draw.rect(screen, (240, 240, 240), box_rect)
    pygame.draw.rect(screen, BLACK, box_rect, 2)

    text1 = font_medium.render("Opponent requests undo", True, BLACK)
    text2 = font_small.render("Allow undo of their last move?", True, BLACK)
    screen.blit(text1, text1.get_rect(center=(WIDTH // 2, box_rect.top + 55)))
    screen.blit(text2, text2.get_rect(center=(WIDTH // 2, box_rect.top + 95)))

    undo_accept_button.draw(screen, font_small)
    undo_reject_button.draw(screen, font_small)

# 胜负与重开
def display_winner(screen, winner):
    if winner == 1:
        text = font_large.render("Black Wins!", True, RED)
    elif winner == 2:
        text = font_large.render("White Wins!", True, RED)
    elif winner == 0:
        text = font_large.render("Draw!", True, RED)

    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))

    s = pygame.Surface((WIDTH, 200), pygame.SRCALPHA)
    s.fill((0, 0, 0, 180))
    screen.blit(s, (0, HEIGHT // 2 - 80))

    screen.blit(text, text_rect)

    restart_button.draw(screen, font_medium)
