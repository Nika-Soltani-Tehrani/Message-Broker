import socket
import threading


class ClientNode:
    def __init__(self):
        self.node = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port_and_ip = ('127.0.0.1', 1373)
        self.node.connect(port_and_ip)
        self.connect = True
        print("In case you want to subscribe to some topics please enter your request like: ")
        print("host>port>subscribe>topic_1>topic_2>...>topic_n ")
        print("In case you want to publish a message please enter your request like: ")
        print("host>port>publish>topic>message")

    def send_message(self, message):
        self.node.sendall(message.encode())

    def receive_message(self):
        data = self.node.recv(1024).decode()
        print(data)

    def main(self):
        while self.connect:
            message = input()
            self.send_message(message)
            if message == "disconnect":
                self.connect = False


Client = ClientNode()
always_receive = threading.Thread(target=Client.receive_message)
always_receive.start()
Client.main()
