import socket
import asyncio
from typing import Dict, List, Tuple

HOST, PORT = "0.0.0.0", 5000

# 房间与连接管理
rooms: Dict[int, List[Tuple[socket.socket, tuple]]] = {}  # room_id -> [(conn, addr)]
addr2room: Dict[tuple, int] = {}                          # addr -> room_id


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
                await dispatch(conn, addr, line.decode("utf-8", "ignore"))
    except Exception:
        # 简化处理：忽略异常，走清理流程
        pass
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

    if typ == "JOIN":  # TODO 房间号输入 等待界面
        try:
            room = int(body)
        except ValueError:
            await send_line(conn, "NULL房间号非法")
            return
        lst = rooms.setdefault(room, [])  # dict方法，返回的是value
        # 去重：同一 addr 重复 JOIN 先移除 TODO 为什么要这样做？直接发给客户你已在房间不行吗？
        for i, (c, a) in enumerate(list(lst)):
            if a == addr:
                lst.pop(i)
                break
        if len(lst) >= 2:
            await send_line(conn, "NULL房间已满")
            return
        lst.append((conn, addr))  # 列表重载=的时候是引用的方式
        addr2room[addr] = room
        print(f"地址 {addr} 加入房间 {room}")
        if len(lst) == 2:
            # 两人齐，开始
            for c, _a in lst:
                await send_line(c, "STAR另一位玩家已连接，游戏开始！")
        else:
            await send_line(conn, "WAIT等待另一位玩家加入房间...")  # client自己分配为玩家1

    elif typ == "MOVE":
        room = addr2room.get(addr)
        if room is None or room not in rooms:
            await send_line(conn, "NULL你不在任何房间中")
            return
        # TODO 客户端实现：收到服务器响应前，无法继续落子
        for c, a in rooms[room]:  # 转发走子信息给对手
            if a != addr:
                await send_line(c, "MOVE" + body)

    elif typ == "EXIT":
        await leave_room(conn, addr)

    elif typ == "CANC":
        # 客户端主动取消等待/退出房间
        # 可选校验 body 的房间号，这里直接按连接维度退出
        await leave_room(conn, addr)
        await send_line(conn, "EXIT已取消匹配")

    else:
        await send_line(conn, "NULL未知指令")


async def leave_room(conn: socket.socket, addr: tuple) -> None:
    room = addr2room.pop(addr, None)
    if room is None:
        return
    lst = rooms.get(room, [])
    # 过滤掉自己
    new_lst = [(c, a) for (c, a) in lst if a != addr]
    rooms[room] = new_lst
    # 通知对手
    for c, _a in new_lst:
        await send_line(c, "EXIT对手已退出游戏")  # TODO 回退上一界面
    # 房间空则删除
    if not new_lst:
        rooms.pop(room, None)


async def main() -> None:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(128)
    print(f"服务器启动于 {HOST}:{PORT}")
    try:
        await accept_loop(server)
    finally:
        try:
            server.close()
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())
