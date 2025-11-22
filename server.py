import socket
import asyncio
from typing import Dict, List, Tuple
from macro import PORT

# 房间与连接管理
rooms: Dict[int, List[Tuple[socket.socket, tuple]]] = {}  # room_id -> [(conn, addr)]
addr2room: Dict[tuple, int] = {}                          # addr -> room_id
protected_rooms: set = set()                              # 保护中的房间号（重开过程中）
restarting_rooms: Dict[int, set[tuple]] = {}


async def send_line(conn: socket.socket, text: str) -> None:
    data = (text.rstrip("\n") + "\n").encode("utf-8", "ignore")  # 确保末尾仅一个换行，使换行成为EOF
    await asyncio.to_thread(conn.sendall, data)


async def accept_loop(server_sock: socket.socket) -> None:
    while True:
        conn, addr = await asyncio.to_thread(server_sock.accept)
        asyncio.create_task(handle_client(conn, addr))


async def handle_client(conn: socket.socket, addr: tuple) -> None:
    try:
        await send_line(conn, "OK欢迎")
        buffer = b""
        while True:  # TCP协议，数据可能分片到达
            chunk = await asyncio.to_thread(conn.recv, 4096)
            if not chunk:
                print("No chunk")
                break
            print("Received chunk:", chunk)
            buffer += chunk
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)  # line是第一个换行符前的内容，剩余内容依旧被buffer缓存
                line = line.decode("utf-8", "ignore")
                typ = line[:4]

                if typ == 'REST':  # 不优雅，但是复用了
                    room = addr2room.get(addr)
                    if room is None:
                        # 第一个用户重开删掉之后，在dispatch创建之前(并不指CANC了)
                        # 第二个用户尝试addr2room.get会进入该分支
                        # 所以不能单纯地扔掉，而是判断一下是否在重开房间号里
                        body = line[4:].strip()
                        try:
                            guess_room = int(body)
                        except ValueError:
                            await send_line(conn, "NULL你不在任何房间中")
                            continue
                        # 如果这个房间正在重开，而且这个 addr 在重开名单里，就允许把 REST 当成 JOIN 来处理
                        if guess_room in restarting_rooms and addr in restarting_rooms[guess_room]:
                            line = 'JOIN' + line[4:]
                        else:
                            await send_line(conn, "NULL你不在任何房间中")
                            continue
                    elif room not in rooms:  # 说明对手重开后又退出了
                        line = 'JOIN' + line[4:]  # str不可变
                    elif len(rooms[room]) == 2:  # 说明该请求是房间内的第一个重开请求
                        # 删除房间里的列表
                        addr1 = rooms[room][0][1]
                        addr2 = rooms[room][1][1]
                        del rooms[room]
                        # 删除 addr2room 中所有指向这个房间的条目
                        for key, value in list(addr2room.items()):
                            if value == room:
                                del addr2room[key]
                        # 在重开过程中保护房间号
                        protected_rooms.add(room)
                        restarting_rooms[room] = {addr1, addr2}
                        line = 'JOIN' + line[4:]
                    elif len(rooms[room]) == 1:  # 房间中有一个人，又收到重开请求，说明是第二个重开请求
                        line = 'JOIN' + line[4:]
                await dispatch(conn, addr, line)
    except Exception:
        pass  # 确保服务器运行
    finally:
        await leave_room(conn, addr)
        try:
            conn.close()
        except Exception:
            pass


async def dispatch(conn: socket.socket, addr: tuple, line: str) -> None:
    print(f"From {addr}: {line}")
    if len(line) < 4:
        await send_line(conn, "NULL消息格式错误")
        return
    typ = line[:4]
    body = line[4:].strip()

    if typ == "JOIN":  # 加入房间
        try:
            room = int(body)
        except ValueError:
            await send_line(conn, "NULL房间号非法")
            return
        lst = rooms.setdefault(room, [])  # dict方法，返回的是value
        # 去重：同一 addr 重复 JOIN 先移除 好处在于维护了FIFO
        for i, (c, a) in enumerate(list(lst)):
            if a == addr:
                lst.pop(i)
                break
        # 1）如果房间在重开保护中：只允许 restarting_rooms 中记录的旧玩家加入
        if room in protected_rooms:
            allowed_addrs = restarting_rooms.get(room, set())
            if addr not in allowed_addrs:
                await send_line(conn, "NULL房间已满")
                return
        # 2）容量限制：非保护状态下，最多两人
        elif len(lst) >= 2:
            await send_line(conn, "NULL房间已满")
            return
        lst.append((conn, addr))
        addr2room[addr] = room  # 若已有则覆盖
        print(f"地址 {addr} 加入房间 {room}")
        if len(lst) == 2:  # 两人齐，开始
            protected_rooms.discard(room)
            restarting_rooms.pop(room, None)  # None: 不存在也不报错
            for c, _a in lst:
                await send_line(c, "STAR另一位玩家已连接，游戏开始！")  # 客户端分配黑棋
        elif len(lst) == 1:
            await send_line(conn, "WAIT等待另一位玩家加入房间...")

    elif typ == "MOVE":  # 落子
        room = addr2room.get(addr)
        if room is None or room not in rooms:
            await send_line(conn, "NULL你不在任何房间中")
            return
        for c, a in rooms[room]:  # 转发走子信息给对手
            if a != addr:
                await send_line(c, "MOVE" + body)

    elif typ == "EXIT":  # 退出
        await leave_room(conn, addr)

    elif typ == "CANC":  # 客户端主动取消等待/退出房间
        await leave_room(conn, addr)  # 会告知另一个玩家

    elif typ == "UNDO":  # 悔棋
        room = addr2room.get(addr)
        if room is None or room not in rooms:
            await send_line(conn, "NULL你不在任何房间中")
            return
        for c, a in rooms[room]:  # 转发悔棋请求给对手
            if a != addr:
                await send_line(c, "UNDO" + body)

    elif typ == "AGRE":  # 对手同意悔棋
        room = addr2room.get(addr)
        if room is None or room not in rooms:
            await send_line(conn, "NULL你不在任何房间中")
            return
        for c, a in rooms[room]:
            if a != addr:
                await send_line(c, "AGRE" + body)

    elif typ == "DAGR":  # 对手拒绝悔棋
        room = addr2room.get(addr)
        if room is None or room not in rooms:
            await send_line(conn, "NULL你不在任何房间中")
            return
        for c, a in rooms[room]:
            if a != addr:
                await send_line(c, "DAGR" + body)

    else:
        await send_line(conn, "NULL未知指令")

    print('after dispatch')
    print('rooms:')
    print(rooms)
    print('addr2room:')
    print(addr2room)


async def leave_room(conn: socket.socket, addr: tuple) -> None:
    room = addr2room.pop(addr, None)
    if room is None:
        return
    protected_rooms.discard(room)
    lst = rooms.get(room, [])
    new_lst = [(c, a) for (c, a) in lst if a != addr]
    rooms[room] = new_lst  # 删掉自己
    # 通知对手
    for c, _a in new_lst:
        await send_line(c, "EXIT")
    # 房间空则删除
    if not new_lst:
        rooms.pop(room, None)
        restarting_rooms.pop(room, None)


async def main() -> None:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 避免进入TIME_WAIT
    server.bind(("0.0.0.0", PORT))  # 监听本机所有网络接口
    server.listen(128)  # 用户上限
    print(f"服务器启动于 {"0.0.0.0"}:{PORT}")
    try:
        await accept_loop(server)
    finally:
        try:
            server.close()
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())
