import pygame
import sys
import numpy as np
import os
import threading
from collections import deque
import socket

from macro import *
from button import *
from frontend import *
from aiagent import AIagent

# ============================================================================
# 后端全局变量
# ============================================================================

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

# 人机模式下：玩家与电脑的棋子颜色（1: 黑, 2: 白）
human_color = 1
ai_color = 2

ai_agent = AIagent(chess_len=LINE_COUNT, player_color=2, difficulty=ai_difficulty)

# 初始化棋盘
board = np.zeros((LINE_COUNT, LINE_COUNT), dtype=int)

# PVC: 当前落子玩家 (1: 黑棋, 2: 白棋)
# PVP: 当前玩家棋色
current_player = 2
game_over = False
winner = 0  # 0: 平局, 1: 黑胜, 2: 白胜

# 悔棋功能相关变量
move_history = []  # 记录每一步的落子位置

# ==== Room Number Input state ====
room_input_text = ""
room_input_active = False  # 点击输入框后变为 True
room_input_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 10, 300, 50)
room_hint_color = (50, 50, 50)
room_border_color_idle = (120, 120, 120)
room_border_color_active = (0, 120, 215)

recv_queue = deque()     # 后台读线程把完整一行消息放进来
room_waiting = False     # 是否处于等待另一位玩家
current_room_num = None  # 当前加入/等待的房间号

wait_opponent = True     # 是否等待对手落子(线上用)

# 人人对战悔棋协议相关状态
undo_request_pending = False  # 已向对手发出悔棋请求，等待对方回应
undo_rejected = False         # 上一次悔棋已被对方拒绝，在对方落子前不能再次请求
undo_dialog_visible = False   # 收到对手的悔棋请求，弹出确认对话框期间为 True

# ============================================================================
# 函数
# ============================================================================

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
    # 重置游戏结束状态
    game_over = False
    winner = 0
    return True

def undo_pvc_move_pair():
    """
    人机模式悔棋：一次撤销“玩家上一手 + 电脑上一手”
    要求：当前不是结束状态，且最后一步是电脑落子
    """
    global board, move_history, current_player, game_over, winner, COMPUTER_MOVE
    global human_color, ai_color

    if game_over:
        return False
    if len(move_history) < 2:
        return False
    # 检查最后一步是否为电脑颜色
    last_row, last_col = move_history[-1]
    if board[last_row][last_col] != ai_color:
        # 不符合预期（例如刚开局还没有AI落子），不执行人机悔棋
        return False
    # 1) 撤销电脑上一手
    row_ai, col_ai = move_history.pop()
    board[row_ai][col_ai] = 0
    # 2) 撤销玩家上一手
    row_h, col_h = move_history.pop()
    # 正常情况下这里就是玩家的棋；为稳妥起见，直接清空
    board[row_h][col_h] = 0
    # 撤销后轮到玩家落子
    current_player = human_color
    game_over = False
    winner = 0
    COMPUTER_MOVE = False
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

def check_full():  # 检查棋盘是否已满
    return np.all(board != 0)

def reset_game():
    """重置游戏"""
    global board, current_player, game_over, winner, move_history, ai_color, COMPUTER_MOVE
    global wait_opponent, undo_request_pending, undo_rejected, undo_dialog_visible
    board = np.zeros((LINE_COUNT, LINE_COUNT), dtype=int)
    if game_mode == PVC_MODE:
        current_player = 1
        if ai_color == 1:
            COMPUTER_MOVE = True
    game_over = False
    winner = 0

    # 重置人人对战悔棋相关状态
    undo_request_pending = False
    undo_rejected = False
    undo_dialog_visible = False

    move_history = []

    # 重置AI状态
    if 'ai_agent' in globals():
        ai_agent.reset()



def computer_move():
    """
    电脑AI落子函数
    使用Minimax算法+Alpha-Beta剪枝
    """
    global board, current_player, ai_color
    
    # 确保是电脑的回合
    if current_player != ai_color:
        return None
        
    # 获取最佳移动
    best_move = ai_agent.findBestChess(board, ai_color)
    
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


def reader(conn: socket.socket):  # 读取服务器消息，逐行放入队列
    try:
        buf = b""
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                recv_queue.append("CONN_CLOSED")
                break
            buf += chunk
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                msg = line.decode("utf-8", "ignore").strip()
                recv_queue.append(msg)
    except Exception as e:
        recv_queue.append(f"ERR{e}")
    finally:
        try: conn.close()
        except: pass

# ============================================================================
# 主程序
# ============================================================================

# 添加时钟控制帧率
clock = pygame.time.Clock()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
t = threading.Thread(target=reader, args=(client,), daemon=True)
t.start()

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
            board[row][col] = ai_color
            move_history.append((row, col))

            if check_win(row, col, ai_color):
                game_over = True
                winner = ai_color

            elif check_full():
                game_over = True
                winner = 0  # 平局

            # 轮到另一方
            current_player = 3 - ai_color

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
                    current_player = 2      # 默认认为自己是玩家2（白）
                    wait_opponent = True    # 默认在等对手先手
                    game_mode = PVP_MODE
                    game_state = ROOM_NUMBER_INPUT
                    reset_game()
                elif pvc_button.check_hover(mouse_pos):
                    game_mode = PVC_MODE
                    current_player = 1  # 默认先手
                    game_state = DIFFICULTY_SELECT
                elif back_button.check_hover(mouse_pos):
                    game_state = TITLE_SCREEN

            elif game_state == ROOM_NUMBER_INPUT:
                if not room_waiting:
                    # 点击输入框激活
                    if room_input_rect.collidepoint(mouse_pos):
                        room_input_active = True
                    else:
                        room_input_active = False

                    # 点击 Send
                    if send_button.check_hover(mouse_pos):
                        try:
                            rn = int(room_input_text.strip())
                        except Exception:
                            room_input_text = ""
                        else:
                            client.sendall(f"JOIN{rn}\n".encode("utf-8"))
                            current_room_num = rn
                            room_waiting = True
                            room_input_active = False

                    # 返回模式选择
                    elif back_button.check_hover(mouse_pos):
                        room_input_text = ""
                        room_input_active = False
                        game_state = MODE_SELECT
                else:
                    # 等待界面：只有退出
                    if back_button.check_hover(mouse_pos):
                        if current_room_num is not None:
                            try:
                                client.sendall(f"CANC{current_room_num}\n".encode("utf-8"))
                                current_player = 2
                                wait_opponent = True
                            except Exception:
                                pass
                        # 重置
                        room_waiting = False
                        current_room_num = None
                        room_input_text = ""
                        game_state = MODE_SELECT

            # 难度选择界面
            elif game_state == DIFFICULTY_SELECT:
                if easy_button.check_hover(mouse_pos):
                    ai_difficulty = EASY
                    ai_agent.set_difficulty(EASY)
                    # 难度选好后，进入执棋颜色选择
                    game_state = SIDE_SELECT
                elif medium_button.check_hover(mouse_pos):
                    ai_difficulty = MEDIUM
                    ai_agent.set_difficulty(MEDIUM)
                    game_state = SIDE_SELECT
                elif hard_button.check_hover(mouse_pos):
                    ai_difficulty = HARD
                    ai_agent.set_difficulty(HARD)
                    game_state = SIDE_SELECT
                elif difficulty_back_button.check_hover(mouse_pos):
                    game_state = MODE_SELECT

            elif game_state == SIDE_SELECT:
                if choose_black_button.check_hover(mouse_pos):
                    # 玩家执黑，电脑执白
                    human_color = 1
                    ai_color = 2
                    ai_agent = AIagent(chess_len=LINE_COUNT, player_color=ai_color, difficulty=ai_difficulty)
                    game_state = GAME_PLAYING
                    reset_game()
                elif choose_white_button.check_hover(mouse_pos):
                    # 玩家执白，电脑执黑
                    human_color = 2
                    ai_color = 1
                    ai_agent = AIagent(chess_len=LINE_COUNT, player_color=ai_color, difficulty=ai_difficulty)
                    game_state = GAME_PLAYING
                    reset_game()
                elif side_back_button.check_hover(mouse_pos):
                    # 返回难度选择
                    game_state = DIFFICULTY_SELECT

            # 游戏进行中
            elif game_state == GAME_PLAYING:
                # 如果当前有对手悔棋确认对话框，优先处理它，其它点击忽略
                if game_mode == PVP_MODE and undo_dialog_visible:
                    if undo_accept_button.check_hover(mouse_pos):
                        if not game_over and move_history:
                            # 对手请求撤销的是他刚才的一步
                            undo_move()
                            # 撤销后轮到对手重新落子
                            wait_opponent = True
                        undo_dialog_visible = False
                        if current_room_num is not None:
                            client.sendall(f"AGRE{current_room_num}\n".encode("utf-8"))
                    elif undo_reject_button.check_hover(mouse_pos):
                        undo_dialog_visible = False
                        if current_room_num is not None:
                            client.sendall(f"DAGR{current_room_num}\n".encode("utf-8"))
                    continue  # 对话框弹出时，其余点击直接丢弃

                if exit_button.check_hover(mouse_pos):
                    game_state = TITLE_SCREEN
                    if game_mode == PVP_MODE:
                        client.sendall(f"CANC{current_room_num}\n".encode("utf-8"))
                        current_player = 2
                        wait_opponent = True
                    reset_game()
                
                elif game_over and restart_button.check_hover(mouse_pos):
                    if game_mode == PVP_MODE:
                        client.sendall(f"REST{current_room_num}\n".encode("utf-8"))
                        room_waiting = True
                    reset_game()
                    game_state = ROOM_NUMBER_INPUT if game_mode == PVP_MODE else DIFFICULTY_SELECT
                    current_player = 2 if game_mode == PVP_MODE else 1  # PVP默认后手, PVC将黑棋设为先手
                    if game_mode == PVP_MODE:
                        wait_opponent = True
                
                elif undo_button.check_hover(mouse_pos) and move_history and not game_over:
                    if game_mode == PVP_MODE:
                        # 只能刚刚落子的一方发起悔棋：
                        #   1) 当前处于等待对手落子（刚下完自己的棋）
                        #   2) 本轮尚未发送悔棋请求，且未被拒绝
                        if not wait_opponent:
                            pass  # 轮到自己走时不能悔棋
                        elif undo_request_pending or undo_dialog_visible or undo_rejected:
                            pass  # 正在等待回应，或本轮已经被拒绝
                        else:
                            # 最后一步必须是自己下的
                            last_row, last_col = move_history[-1]
                            if board[last_row][last_col] == current_player:
                                undo_request_pending = True
                                if current_room_num is not None:
                                    client.sendall(f"UNDO{current_room_num}\n".encode("utf-8"))
                            # 否则不做任何事
                    elif game_mode == PVC_MODE:
                        undo_pvc_move_pair()
                
                elif not game_over:
                    if game_mode == PVP_MODE:  # 正在等待对手落子/处理悔棋，忽略点击
                        if wait_opponent or undo_request_pending or undo_dialog_visible: continue
                    x, y = mouse_pos
                    col = round((x - GRID_SIZE) / GRID_SIZE)
                    row = round((y - GRID_SIZE) / GRID_SIZE)

                    if 0 <= row < LINE_COUNT and 0 <= col < LINE_COUNT:
                        if board[row][col] == 0:
                            if game_mode == PVP_MODE:
                                client.sendall(f"MOVE{row},{col}\n".encode("utf-8"))
                                wait_opponent = True
                            board[row][col] = current_player
                            move_history.append((row, col))
                            if check_win(row, col, current_player):
                                game_over = True
                                winner = current_player
                            elif check_full():
                                game_over = True
                                winner = 0  # 平局
                            if game_mode == PVC_MODE:  # 人机轮换
                                current_player = 3 - current_player
                                if not game_over and current_player == ai_color:
                                    COMPUTER_MOVE = True
                                    continue

        if event.type == pygame.KEYDOWN:
            if game_state == ROOM_NUMBER_INPUT and room_input_active:
                if event.key == pygame.K_RETURN:
                    text = room_input_text.strip()
                    if not text:  # 无法转化的输入处理为空
                        room_input_text = ""
                    else:
                        try:
                            rn = int(text)
                        except Exception:
                            room_input_text = ""
                        else:
                            if game_mode == PVP_MODE:  # 保险
                                client.sendall(f"JOIN{rn}\n".encode("utf-8"))
                            current_room_num = rn
                            room_waiting = True
                            room_input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    room_input_text = room_input_text[:-1]
                else:  # 只接受可见字符，随后由 int 校验
                    ch = event.unicode
                    if ch and 32 <= ord(ch) <= 126:
                        room_input_text += ch

    # 处理后台读线程入队的服务器消息
    while recv_queue:
        msg = recv_queue.popleft()
        tpe = msg[:4]

        if tpe == "WAIT":
            # 保持在房间输入界面但进入等待态
            room_waiting = True
            game_state = ROOM_NUMBER_INPUT
            current_player = 1  # 自己是玩家1，先手
            wait_opponent = False

        elif tpe == "STAR":
            # 配对完成，开始游戏
            room_waiting = False
            reset_game()
            game_state = GAME_PLAYING

        elif tpe == "MOVE":
            # 对手落子
            body = msg[4:]
            try:
                row_str, col_str = body.split(",")
                row = int(row_str)
                col = int(col_str)
            except Exception:
                continue
            else:
                if 0 <= row < LINE_COUNT and 0 <= col < LINE_COUNT:
                    opponent_color = 3 - current_player
                    board[row][col] = opponent_color
                    move_history.append((row, col))
                    if check_win(row, col, opponent_color):
                        game_over = True
                        winner = opponent_color
                    elif check_full():
                        game_over = True
                        winner = 0  # 平局
                    wait_opponent = False  # 对手已落子，结束等待状态
                    undo_rejected = False  # 新一轮开始，可以重新发起悔棋请求

        elif tpe == "NULL":
            # 非法或失败。清空输入，回到可输入态
            # TODO 前端显示
            room_waiting = False
            current_room_num = None
            room_input_text = ""

        elif tpe == "UNDO":
            # 收到对手的悔棋请求：弹出确认对话框
            if game_mode == PVP_MODE and not game_over:
                undo_dialog_visible = True

        elif tpe == "AGRE":
            # 对手同意悔棋：撤销自己刚才的一步
            if game_mode == PVP_MODE and undo_request_pending and not game_over and move_history:
                undo_move()
                undo_request_pending = False
                undo_rejected = False
                # 撤销后轮到自己重新落子
                wait_opponent = False

        elif tpe == "DAGR":
            # 对手拒绝悔棋：在对方落子前不能再次发起
            if game_mode == PVP_MODE and undo_request_pending:
                undo_request_pending = False
                undo_rejected = True

        elif tpe == "EXIT":
            # 对手退出；无论在等或在玩，回到等待状态
            reset_game()
            room_waiting = True
            # current_room_num = None
            game_state = ROOM_NUMBER_INPUT
            current_player = 1  # 自己是玩家1，先手
            wait_opponent = False

        elif msg == "CONN_CLOSED" or msg.startswith("ERR"):
            # 连接断开或错误，退回标题
            room_waiting = False
            current_room_num = None
            game_state = TITLE_SCREEN

    # 更新按钮悬停状态
    # 前段代码如果没有事件触发的话，就不会check_hover，导致前端无渲染效果
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
        if game_mode == PVP_MODE and undo_dialog_visible:
            undo_accept_button.check_hover(mouse_pos)
            undo_reject_button.check_hover(mouse_pos)
    elif game_state == ROOM_NUMBER_INPUT:
        if not room_waiting:
            send_button.check_hover(mouse_pos)
        back_button.check_hover(mouse_pos)
    elif game_state == SIDE_SELECT:
        choose_black_button.check_hover(mouse_pos)
        choose_white_button.check_hover(mouse_pos)
        side_back_button.check_hover(mouse_pos)

    # 绘制当前界面
    if game_state == TITLE_SCREEN:
        draw_title_screen(screen)
    elif game_state == MODE_SELECT:
        draw_mode_select(screen)
    elif game_state == DIFFICULTY_SELECT:
        draw_difficulty_select(
            screen,
            easy_button,
            medium_button,
            hard_button,
            difficulty_back_button,
        )
    elif game_state == SIDE_SELECT:
        draw_side_select(
            screen,
            choose_black_button,
            choose_white_button,
            side_back_button,
        )
    elif game_state == GAME_PLAYING:
        draw_board(screen)
        draw_pieces(screen, board)
        draw_game_info(
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
        )
        if game_mode == PVP_MODE and undo_dialog_visible:
            draw_undo_dialog(screen)
        if game_over:
            display_winner(screen, winner)
    elif game_state == ROOM_NUMBER_INPUT:
        draw_room_number_input(
            screen,
            room_waiting,
            room_input_active,
            room_input_rect,
            room_input_text,
            room_hint_color,
            room_border_color_idle,
            room_border_color_active,
        )

    pygame.display.flip()
    clock.tick(10)

pygame.quit()
sys.exit()