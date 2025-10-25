import socket
import threading
import time
import sys

HOST = "10.81.56.145"   # 改成你的服务器IP
PORT = 5000
ROOM = 1                # 加入的房间号
AUTO = False            # True=自动测试，False=交互

def send_line(conn: socket.socket, text: str) -> None:
    data = (text.rstrip("\n") + "\n").encode("utf-8", "ignore")
    conn.sendall(data)

def reader(conn: socket.socket):
    try:
        buf = b""
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                print("对端关闭")
                break
            buf += chunk
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                print("<", line.decode("utf-8", "ignore"))
                # TODO 根据服务器消息做相应处理
    except Exception as e:
        print("读错误：", e)
    finally:
        try: conn.close()
        except: pass
        os__exit()

def writer_interactive(conn: socket.socket):
    try:
        # 只发一次 JOIN
        send_line(conn, f"JOIN{ROOM}")
        for line in sys.stdin:  # 一直loop直到输入exit
            line = line.strip()
            if not line:
                continue
            if line.lower() == "exit":
                send_line(conn, "EXIT")
                break
            # 其他内容按 MOVE 发送
            send_line(conn, "MOVE" + line)
        time.sleep(0.2)
    except Exception as e:
        print("写错误：", e)
    finally:
        try: conn.shutdown(socket.SHUT_RDWR)
        except: pass

def writer_auto(conn: socket.socket):
    try:
        send_line(conn, f"JOIN{ROOM}")
        # 等待开局提示后发几步棋
        time.sleep(1.0)
        for payload in ["x=7,y=7", "x=8,y=7", "x=9,y=7"]:
            send_line(conn, "MOVE" + payload)
            time.sleep(0.5)
        send_line(conn, "EXIT")
        time.sleep(0.2)
    except Exception as e:
        print("写错误：", e)
    finally:
        try: conn.shutdown(socket.SHUT_RDWR)
        except: pass

def os__exit():
    # 让主线程尽快退出
    try:
        import os
        os._exit(0)
    except Exception:
        sys.exit(0)

def main():
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((HOST, PORT))
    # 启动读线程
    t = threading.Thread(target=reader, args=(conn,), daemon=True)
    t.start()
    # 发送欢迎后的动作
    if AUTO:
        writer_auto(conn)
    else:
        print("已连接。输入内容后按回车发送 MOVE；输入 exit 发送 EXIT 退出。")
        writer_interactive(conn)
    t.join(timeout=2)

if __name__ == "__main__":
    main()
