import socket
# 1.创建socket
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2. 链接服务器
#server_addr = ("10.106.40.231", 2000)
server_addr = ("127.0.0.1", 2000)
tcp_socket.connect(server_addr)

# 3. 发送数据
send_data = input("请输入要发送的数据：")
while send_data != '':
    tcp_socket.send(send_data.encode("utf8"))
    send_data = input("请输入要发送的数据：")
# 4. 关闭套接字
tcp_socket.close()
