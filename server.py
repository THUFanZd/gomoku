import socket

HOST = '0.0.0.0'  # 监听所有网卡
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(2)

print("等待两个玩家连接...")
conn1, addr1 = server.accept()
print(conn1)
print("玩家1已连接：", addr1)
conn1.sendall("你是玩家1，等待另一位玩家...\n".encode("utf-8"))

conn2, addr2 = server.accept()
print(conn2)
print("玩家2已连接：", addr2)
conn2.sendall("你是玩家2，游戏开始！\n".encode("utf-8"))
conn1.sendall("另一位玩家已连接，游戏开始！\n".encode("utf-8"))

# 转发消息
while True:
    data = conn1.recv(1024)
    if not data:
        break
    conn2.sendall(data)

    data = conn2.recv(1024)
    if not data:
        break
    conn1.sendall(data)
