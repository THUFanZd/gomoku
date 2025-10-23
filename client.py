import socket

HOST = '192.168.196.97'  # 这里填服务器电脑的局域网IP
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

print(client.recv(1024).decode())

while True:
    msg = input("你要发送的消息：")
    client.sendall(msg.encode())
    data = client.recv(1024)
    print("收到:", data.decode())
