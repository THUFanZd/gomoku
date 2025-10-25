from macro import *

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