import pygame
import sys
import numpy as np
import os
import time
from macro import *
from button import Button
from backend import *
from frontend import *


# 初始化pygame
pygame.init()

# 创建游戏窗口
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("五子棋")

# 设置窗口居中
os.environ['SDL_VIDEO_CENTERED'] = '1'
game_state = TITLE_SCREEN

# 游戏模式
game_mode = PVP_MODE
ai_difficulty = MEDIUM  # 默认难度

# 初始化棋盘
board = np.zeros((LINE_COUNT, LINE_COUNT), dtype=int)

# 当前玩家 (1: 黑棋, 2: 白棋)
current_player = 1
game_over = False
winner = 0

# 悔棋功能相关变量
move_history = []  # 记录每一步的落子位置

# 创建按钮
start_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 60, "START", GREEN, (100, 200, 100))
title_exit_button = Button(WIDTH//2 - 100, HEIGHT//2 + 130, 200, 60, "EXIT GAME", RED, (255, 100, 100))
pvp_button = Button(WIDTH // 2 - 150, HEIGHT // 2, 300, 60, "Player vs Player", BLUE, (100, 100, 255))
pvc_button = Button(WIDTH // 2 - 150, HEIGHT // 2 + 80, 300, 60, "Player vs Computer", GREEN, (100, 200, 100))
back_button = Button(20, HEIGHT - 70, 100, 40, "Back", RED, (255, 100, 100))
undo_button = Button(WIDTH - 245, 5, 100, 40, "Undo", BLUE, (100, 100, 255))
restart_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 50, "Restart", WHITE, GRAY, BLACK)
exit_button = Button(WIDTH - 120, 5, 100, 40, "EXIT", RED, (255, 100, 100))

# 难度选择按钮
easy_button = Button(WIDTH // 2 - 150, HEIGHT // 2 - 60, 300, 60, "Easy", GREEN, (100, 200, 100))
medium_button = Button(WIDTH // 2 - 150, HEIGHT // 2 + 20, 300, 60, "Medium", BLUE, (100, 100, 255))
hard_button = Button(WIDTH // 2 - 150, HEIGHT // 2 + 100, 300, 60, "Hard", RED, (255, 100, 100))
difficulty_back_button = Button(20, HEIGHT - 70, 100, 40, "Back", RED, (255, 100, 100))



# 初始化不同大小的字体
font_small = init_font(24)
font_medium = init_font(36)
font_large = init_font(72)
font_title = init_font(96)

# 绘制标题画面
def draw_title_screen():
    """绘制游戏标题画面"""
    screen.fill(BROWN)

    # 绘制游戏标题
    title_text = font_title.render("Gomoku Game", True, BLACK)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(title_text, title_rect)

    # 绘制开始按钮
    start_button.draw(screen, font_medium)
    # 绘制退出按钮
    title_exit_button.draw(screen, font_medium)

    # 绘制提示文字
    hint_text = font_small.render("Click to start or exit.", True, BLACK)
    hint_rect = hint_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 300))
    screen.blit(hint_text, hint_rect)

# 绘制模式选择界面
def draw_mode_select():
    """绘制游戏模式选择界面"""
    screen.fill(BROWN)

    # 绘制标题
    title_text = font_large.render("Mode", True, BLACK)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    screen.blit(title_text, title_rect)

    # 绘制模式选择按钮
    pvp_button.draw(screen, font_medium)
    pvc_button.draw(screen, font_medium)

    # 绘制返回按钮
    back_button.draw(screen, font_small)

    # 绘制说明文字
    desc_text = font_small.render("Player vs Player: Two players take turns", True, BLACK)
    desc_rect = desc_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 300))
    screen.blit(desc_text, desc_rect)

    desc_text2 = font_small.render("Player vs Computer: Play against AI", True, BLACK)
    desc_rect2 = desc_text2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 330))
    screen.blit(desc_text2, desc_rect2)

# 绘制难度选择界面
def draw_difficulty_select():
    """绘制难度选择界面"""
    screen.fill(BROWN)
    
    # 绘制标题
    title_text = font_large.render("Select Difficulty", True, BLACK)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    screen.blit(title_text, title_rect)
    
    # 绘制难度选择按钮
    easy_button.draw(screen, font_medium)
    medium_button.draw(screen, font_medium)
    hard_button.draw(screen, font_medium)
    
    # 绘制返回按钮
    difficulty_back_button.draw(screen, font_small)
    
    # 绘制说明文字
    desc_text = font_small.render("Easy: AI makes quick moves", True, BLACK)
    desc_rect = desc_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 180))
    screen.blit(desc_text, desc_rect)
    
    desc_text2 = font_small.render("Medium: Balanced AI", True, BLACK)
    desc_rect2 = desc_text2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 210))
    screen.blit(desc_text2, desc_rect2)
    
    desc_text3 = font_small.render("Hard: Challenging AI", True, BLACK)
    desc_rect3 = desc_text3.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 240))
    screen.blit(desc_text3, desc_rect3)

# 统计棋子数量
def count_pieces():
    black_count = np.sum(board == 1)
    white_count = np.sum(board == 2)
    return black_count, white_count

def draw_board():
    """绘制棋盘"""
    screen.fill(BROWN)

    # 绘制网格线
    for i in range(LINE_COUNT):
        # 横线
        pygame.draw.line(screen, BLACK,
                         (GRID_SIZE, GRID_SIZE * (i + 1)),
                         (WIDTH - GRID_SIZE, GRID_SIZE * (i + 1)), 2)
        # 竖线
        pygame.draw.line(screen, BLACK,
                         (GRID_SIZE * (i + 1), GRID_SIZE),
                         (GRID_SIZE * (i + 1), HEIGHT - GRID_SIZE), 2)

    # 绘制棋盘上的五个点
    points = [(3, 3), (3, 11), (7, 7), (11, 3), (11, 11)]
    for point in points:
        x, y = point
        pygame.draw.circle(screen, BLACK,
                           (GRID_SIZE * (x + 1), GRID_SIZE * (y + 1)), 5)

def draw_pieces():
    """绘制棋子"""
    for i in range(LINE_COUNT):
        for j in range(LINE_COUNT):
            if board[i][j] == 1:  # 黑棋
                pygame.draw.circle(screen, BLACK,
                                   (GRID_SIZE * (j + 1), GRID_SIZE * (i + 1)),
                                   GRID_SIZE // 2 - 2)
            elif board[i][j] == 2:  # 白棋
                pygame.draw.circle(screen, WHITE,
                                   (GRID_SIZE * (j + 1), GRID_SIZE * (i + 1)),
                                   GRID_SIZE // 2 - 2)

# 绘制游戏状态信息
def draw_game_info():
    """绘制当前玩家、棋子数量和按钮"""
    # 显示当前玩家
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

    # 显示棋子数量
    black_count, white_count = count_pieces()
    count_text = font_small.render(f"Black: {black_count}  White: {white_count}", True, BLACK)
    screen.blit(count_text, (10, 30))

    # 显示游戏模式和难度
    mode_text = font_small.render(f"Mode: {'Player vs Player' if game_mode == PVP_MODE else 'Player vs Computer'}", True, BLACK)
    screen.blit(mode_text, (300, 10))
    
    if game_mode == PVC_MODE:
        difficulty_names = ["Easy", "Medium", "Hard"]
        difficulty_text = font_small.render(f"Difficulty: {difficulty_names[ai_difficulty]}", True, BLACK)
        screen.blit(difficulty_text, (300, 40))

    # 绘制按钮
    if move_history and not game_over:
        undo_button.draw(screen, font_small)
    exit_button.draw(screen, font_small)

# 悔棋功能
def undo_move():
    """悔棋一步"""
    global current_player, game_over, winner

    if not move_history or game_over:
        return False

    # 获取最后一步的位置
    last_row, last_col = move_history.pop()

    # 清空该位置的棋子
    board[last_row][last_col] = 0

    # 切换回上一个玩家
    current_player = 3 - current_player

    # 重置游戏结束状态
    game_over = False
    winner = 0

    return True

def check_win(row, col, player):
    """检查是否有玩家获胜"""
    # 检查方向: 水平、垂直、左上到右下、右上到左下
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

    for dr, dc in directions:
        count = 1  # 当前位置已经有一个棋子

        # 正向检查
        r, c = row + dr, col + dc
        while 0 <= r < LINE_COUNT and 0 <= c < LINE_COUNT and board[r][c] == player:
            count += 1
            r += dr
            c += dc

        # 反向检查
        r, c = row - dr, col - dc
        while 0 <= r < LINE_COUNT and 0 <= c < LINE_COUNT and board[r][c] == player:
            count += 1
            r -= dr
            c -= dc

        # 如果有5个连续的棋子，则获胜
        if count >= 5:
            return True

    return False

def display_winner(winner):
    """显示获胜信息和重启按钮"""
    if winner == 1:
        text = font_large.render("Black Wins!", True, RED)
    else:
        text = font_large.render("White Wins!", True, RED)

    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))

    # 绘制半透明背景
    s = pygame.Surface((WIDTH, 200), pygame.SRCALPHA)
    s.fill((0, 0, 0, 180))
    screen.blit(s, (0, HEIGHT // 2 - 80))

    screen.blit(text, text_rect)

    # 显示重新开始按钮
    restart_button.draw(screen, font_medium)

def reset_game():
    """重置游戏"""
    global board, current_player, game_over, winner, move_history
    board = np.zeros((LINE_COUNT, LINE_COUNT), dtype=int)
    current_player = 1
    game_over = False
    winner = 0
    move_history = []
    # 重置AI状态
    if 'ai_agent' in globals():
        ai_agent.reset()

# ============================================================================
# 人机对战相关函数
# ============================================================================

class AIagent:
    def __init__(self, chess_len=15, player_color=2, difficulty=MEDIUM):
        self.len = chess_len
        self.player = player_color
        self.difficulty = difficulty
        
        # 根据难度设置搜索参数
        if difficulty == EASY:
            self.search_depth = 2
            self.limited_move_num = 10
        elif difficulty == MEDIUM:
            self.search_depth = 3
            self.limited_move_num = 20
        else:  # HARD
            self.search_depth = 4
            self.limited_move_num = 30
            
        # 初始化记录数组
        self.record = [[[0, 0, 0, 0] for _ in range(chess_len)] for _ in range(chess_len)]
        self.count = [[0 for _ in range(8)] for _ in range(2)]
        self.bestmove = None
    
    def set_difficulty(self, difficulty):
        """设置AI难度"""
        self.difficulty = difficulty
        if difficulty == EASY:
            self.search_depth = 2
            self.limited_move_num = 10
        elif difficulty == MEDIUM:
            self.search_depth = 3
            self.limited_move_num = 20
        else:  # HARD
            self.search_depth = 4
            self.limited_move_num = 30
    
    def reset(self):
        """重置AI状态"""
        for y in range(self.len):
            for x in range(self.len):
                for i in range(4):
                    self.record[y][x][i] = 0
        for i in range(len(self.count)):
            for j in range(len(self.count[0])):
                self.count[i][j] = 0

    def hasNeighbor(self, board, x, y, radius=1):
        """检查位置周围是否有棋子"""
        start_x, end_x = max(0, x - radius), min(self.len - 1, x + radius)
        start_y, end_y = max(0, y - radius), min(self.len - 1, y + radius)
        
        for i in range(start_y, end_y + 1):
            for j in range(start_x, end_x + 1):
                if board[i][j] != 0:
                    return True
        return False

    def getLine(self, board, x, y, dir_offset, mine, opponent):
        """获取指定方向的棋子序列"""
        line = [0] * 9
        tmp_x = x - 5 * dir_offset[0]
        tmp_y = y - 5 * dir_offset[1]
        
        for i in range(9):
            tmp_x += dir_offset[0]
            tmp_y += dir_offset[1]
            if tmp_x < 0 or tmp_x >= self.len or tmp_y < 0 or tmp_y >= self.len:
                line[i] = opponent
            else:
                line[i] = board[tmp_y][tmp_x]
        return line

    def analysisLine(self, board, x, y, dir_index, dir_offset, mine, opponent, count):
        """分析一条线上的棋型"""
        def setRecord(left, right):
            tmp_x = x + (-5 + left) * dir_offset[0]
            tmp_y = y + (-5 + left) * dir_offset[1]
            for i in range(left, right + 1):
                tmp_x += dir_offset[0]
                tmp_y += dir_offset[1]
                if 0 <= tmp_x < self.len and 0 <= tmp_y < self.len:
                    self.record[tmp_y][tmp_x][dir_index] = 1

        empty = 0
        left_idx, right_idx = 4, 4
        line = self.getLine(board, x, y, dir_offset, mine, opponent)

        # 向两边扩展找到连续棋子
        while right_idx < 8 and line[right_idx + 1] == mine:
            right_idx += 1
        while left_idx > 0 and line[left_idx - 1] == mine:
            left_idx -= 1

        left_range, right_range = left_idx, right_idx
        while right_range < 8 and line[right_range + 1] != opponent:
            right_range += 1
        while left_range > 0 and line[left_range - 1] != opponent:
            left_range -= 1

        chess_range = right_range - left_range + 1
        if chess_range < 5:
            setRecord(left_range, right_range)
            return

        setRecord(left_idx, right_idx)
        m_range = right_idx - left_idx + 1

        # 判断棋型
        if m_range >= 5:
            count[CHESS_TYPE.LIVE_FIVE] += 1
        elif m_range == 4:
            left_empty = line[left_idx - 1] == empty if left_idx > 0 else False
            right_empty = line[right_idx + 1] == empty if right_idx < 8 else False
            if left_empty and right_empty:
                count[CHESS_TYPE.LIVE_FOUR] += 1
            elif left_empty or right_empty:
                count[CHESS_TYPE.CHONG_FOUR] += 1
        elif m_range == 3:
            left_empty = line[left_idx - 1] == empty if left_idx > 0 else False
            right_empty = line[right_idx + 1] == empty if right_idx < 8 else False
            
            # 检查冲四情况
            left_four = False
            right_four = False
            
            if left_empty and left_idx - 2 >= 0 and line[left_idx - 2] == mine:
                count[CHESS_TYPE.CHONG_FOUR] += 1
                left_four = True
            if right_empty and right_idx + 2 <= 8 and line[right_idx + 2] == mine:
                count[CHESS_TYPE.CHONG_FOUR] += 1
                right_four = True
                
            if left_four or right_four:
                pass
            elif left_empty and right_empty:
                if chess_range >= 5:
                    count[CHESS_TYPE.LIVE_THREE] += 1
                else:
                    count[CHESS_TYPE.SLEEP_THREE] += 1
            elif left_empty or right_empty:
                count[CHESS_TYPE.SLEEP_THREE] += 1

    def evaluatePoint(self, board, x, y, mine, opponent, count=None):
        """评估单个位置的分数"""
        if count is None:
            count = self.count[mine - 1]
            
        dir_offsets = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for i, offset in enumerate(dir_offsets):
            if self.record[y][x][i] == 0:
                self.analysisLine(board, x, y, i, offset, mine, opponent, count)

    def getPointScore(self, count):
        """根据棋型统计计算分数"""
        score = 0
        
        if count[CHESS_TYPE.LIVE_FIVE] > 0:
            return SCORE_FIVE
            
        if count[CHESS_TYPE.LIVE_FOUR] > 0:
            return SCORE_FOUR
            
        if count[CHESS_TYPE.CHONG_FOUR] > 1:
            score += count[CHESS_TYPE.CHONG_FOUR] * SCORE_SFOUR
        elif count[CHESS_TYPE.CHONG_FOUR] > 0 and count[CHESS_TYPE.LIVE_THREE] > 0:
            score += count[CHESS_TYPE.CHONG_FOUR] * SCORE_SFOUR
        elif count[CHESS_TYPE.CHONG_FOUR] > 0:
            score += SCORE_THREE
            
        if count[CHESS_TYPE.LIVE_THREE] > 1:
            score += 5 * SCORE_THREE
        elif count[CHESS_TYPE.LIVE_THREE] > 0:
            score += SCORE_THREE
            
        if count[CHESS_TYPE.SLEEP_THREE] > 0:
            score += count[CHESS_TYPE.SLEEP_THREE] * SCORE_STHREE
        if count[CHESS_TYPE.LIVE_TWO] > 0:
            score += count[CHESS_TYPE.LIVE_TWO] * SCORE_TWO
        if count[CHESS_TYPE.SLEEP_TWO] > 0:
            score += count[CHESS_TYPE.SLEEP_TWO] * SCORE_STWO
            
        return score

    def evaluatePointScore(self, board, x, y, mine, opponent):
        """评估位置对双方的价值"""
        # 重置计数
        for i in range(len(self.count)):
            for j in range(len(self.count[0])):
                self.count[i][j] = 0

        # 评估我方价值
        board[y][x] = mine
        self.evaluatePoint(board, x, y, mine, opponent, self.count[mine - 1])
        mine_score = self.getPointScore(self.count[mine - 1])
        board[y][x] = opponent
        
        # 评估对方价值
        self.evaluatePoint(board, x, y, opponent, mine, self.count[opponent - 1])
        opponent_score = self.getPointScore(self.count[opponent - 1])
        board[y][x] = 0
        
        return mine_score, opponent_score

    def genmove(self, board, turn):
        """生成候选移动位置"""
        if turn == 1:  # 黑棋
            mine, opponent = 1, 2
        else:  # 白棋
            mine, opponent = 2, 1
            
        moves = []
        radius = 1
        
        # 收集所有可能的位置
        for y in range(self.len):
            for x in range(self.len):
                if board[y][x] == 0 and self.hasNeighbor(board, x, y, radius):
                    mine_score, opponent_score = self.evaluatePointScore(board, x, y, mine, opponent)
                    score = max(mine_score, opponent_score)
                    moves.append((score, x, y))
        
        # 按分数排序
        moves.sort(reverse=True)
        
        # 限制移动数量以提高性能
        if len(moves) > self.limited_move_num:
            moves = moves[:self.limited_move_num]
            
        return moves

    def __search(self, board, turn, depth, alpha, beta):
        """Minimax搜索核心算法"""
        # 基础情况：达到深度限制或游戏结束
        if depth <= 0:
            return self.evaluate(board, turn)
            
        moves = self.genmove(board, turn)
        if not moves:
            return self.evaluate(board, turn)
            
        best_score = SCORE_MIN
        opponent = 3 - turn  # 切换玩家
        
        for score, x, y in moves:
            board[y][x] = turn
            current_score = -self.__search(board, opponent, depth - 1, -beta, -alpha)
            board[y][x] = 0
            
            if current_score > best_score:
                best_score = current_score
                if depth == self.search_depth:
                    self.bestmove = (x, y)
                    
            if best_score > alpha:
                alpha = best_score
                
            # Alpha-Beta剪枝
            if alpha >= beta:
                break
                
        return best_score

    def evaluate(self, board, turn):
        """评估整个棋盘状态"""
        self.reset()
        
        if turn == 1:
            mine, opponent = 1, 2
        else:
            mine, opponent = 2, 1
            
        # 统计所有棋子的棋型
        for y in range(self.len):
            for x in range(self.len):
                if board[y][x] == mine:
                    self.evaluatePoint(board, x, y, mine, opponent)
                elif board[y][x] == opponent:
                    self.evaluatePoint(board, x, y, opponent, mine)
        
        # 计算总分
        mine_count = self.count[mine - 1]
        opponent_count = self.count[opponent - 1]
        
        mine_score = self.getPointScore(mine_count)
        opponent_score = self.getPointScore(opponent_count)
        
        return mine_score - opponent_score

    def findBestChess(self, board, turn):
        """找到最佳落子位置"""
        self.bestmove = None
        self.__search(board, turn, self.search_depth, SCORE_MIN, SCORE_MAX)
        return self.bestmove

# 创建AI实例
ai_agent = AIagent(chess_len=LINE_COUNT, player_color=2, difficulty=ai_difficulty)

def computer_move():
    """
    电脑AI落子函数
    使用Minimax算法+Alpha-Beta剪枝
    """
    global board, current_player
    
    # 确保是电脑的回合
    if current_player != 2:
        return None
        
    # 获取最佳移动
    best_move = ai_agent.findBestChess(board, 2)
    
    if best_move:
        x, y = best_move
        return (y, x)  # 返回(row, col)格式
    
    # 如果没有找到最佳移动，随机选择一个空位
    empty_positions = []
    for i in range(LINE_COUNT):
        for j in range(LINE_COUNT):
            if board[i][j] == 0:
                empty_positions.append((i, j))
    
    if empty_positions:
        import random
        return random.choice(empty_positions)
    else:
        return None

# ============================================================================
# 主程序
# ============================================================================

# 添加时钟控制帧率
clock = pygame.time.Clock()

# 主游戏循环
running = True
COMPUTER_MOVE = False
while running:
    mouse_pos = pygame.mouse.get_pos()

    if COMPUTER_MOVE:
        COMPUTER_MOVE = False
        computer_pos = computer_move()
        if computer_pos:
            row, col = computer_pos
            board[row][col] = 2
            move_history.append((row, col))

            if check_win(row, col, 2):
                game_over = True
                winner = 2

            current_player = 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            # 标题画面
            if game_state == TITLE_SCREEN:
                if start_button.check_hover(mouse_pos):
                    game_state = MODE_SELECT
                elif title_exit_button.check_hover(mouse_pos):
                    running = False

            # 模式选择界面
            elif game_state == MODE_SELECT:
                if pvp_button.check_hover(mouse_pos):
                    game_mode = PVP_MODE
                    game_state = GAME_PLAYING
                    reset_game()
                elif pvc_button.check_hover(mouse_pos):
                    game_mode = PVC_MODE
                    game_state = DIFFICULTY_SELECT
                elif back_button.check_hover(mouse_pos):
                    game_state = TITLE_SCREEN

            # 难度选择界面
            elif game_state == DIFFICULTY_SELECT:
                if easy_button.check_hover(mouse_pos):
                    ai_difficulty = EASY
                    ai_agent.set_difficulty(EASY)
                    game_state = GAME_PLAYING
                    reset_game()
                elif medium_button.check_hover(mouse_pos):
                    ai_difficulty = MEDIUM
                    ai_agent.set_difficulty(MEDIUM)
                    game_state = GAME_PLAYING
                    reset_game()
                elif hard_button.check_hover(mouse_pos):
                    ai_difficulty = HARD
                    ai_agent.set_difficulty(HARD)
                    game_state = GAME_PLAYING
                    reset_game()
                elif difficulty_back_button.check_hover(mouse_pos):
                    game_state = MODE_SELECT

            # 游戏进行中
            elif game_state == GAME_PLAYING:
                # 检查按钮点击
                if exit_button.check_hover(mouse_pos):
                    game_state = TITLE_SCREEN
                elif undo_button.check_hover(mouse_pos) and move_history and not game_over:
                    undo_move()
                elif restart_button.check_hover(mouse_pos) and game_over:
                    reset_game()
                elif not game_over:
                    # 棋盘点击逻辑
                    x, y = mouse_pos
                    col = round((x - GRID_SIZE) / GRID_SIZE)
                    row = round((y - GRID_SIZE) / GRID_SIZE)

                    if 0 <= row < LINE_COUNT and 0 <= col < LINE_COUNT:
                        if board[row][col] == 0:
                            board[row][col] = current_player
                            move_history.append((row, col))

                            if check_win(row, col, current_player):
                                game_over = True
                                winner = current_player

                            current_player = 3 - current_player

                            # 人机对战模式：电脑回合
                            if game_mode == PVC_MODE and not game_over and current_player == 2:
                                COMPUTER_MOVE = True
                                continue

    # 更新按钮悬停状态
    if game_state == TITLE_SCREEN:
        start_button.check_hover(mouse_pos)
        title_exit_button.check_hover(mouse_pos)
    elif game_state == MODE_SELECT:
        pvp_button.check_hover(mouse_pos)
        pvc_button.check_hover(mouse_pos)
        back_button.check_hover(mouse_pos)
    elif game_state == DIFFICULTY_SELECT:
        easy_button.check_hover(mouse_pos)
        medium_button.check_hover(mouse_pos)
        hard_button.check_hover(mouse_pos)
        difficulty_back_button.check_hover(mouse_pos)
    elif game_state == GAME_PLAYING:
        if move_history and not game_over:
            undo_button.check_hover(mouse_pos)
        exit_button.check_hover(mouse_pos)
        if game_over:
            restart_button.check_hover(mouse_pos)

    # 绘制当前界面
    if game_state == TITLE_SCREEN:
        draw_title_screen()
    elif game_state == MODE_SELECT:
        draw_mode_select()
    elif game_state == DIFFICULTY_SELECT:
        draw_difficulty_select()
    elif game_state == GAME_PLAYING:
        draw_board()
        draw_pieces()
        draw_game_info()
        if game_over:
            display_winner(winner)

    pygame.display.flip()
    clock.tick(10)

pygame.quit()
sys.exit()