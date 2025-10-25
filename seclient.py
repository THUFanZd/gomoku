import socket

HOST = '10.81.56.145'  # 这里填服务器电脑的局域网IP
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

def send_line(conn: socket.socket, text: str) -> None:
    data = (text.rstrip("\n") + "\n").encode("utf-8", "ignore")  # 确保末尾仅一个换行，使换行成为EOF
    conn.sendall(data)

def recv_line(conn: socket.socket) -> str:
    pass