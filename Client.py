import sys
import time
import socket
import threading


class ClientNode:
    def __init__(self):
        self.node = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # '127.0.0.1', 1373
        port_and_ip = (sys.argv[2], int(sys.argv[3]))
        self.node.connect(port_and_ip)
        self.connect = True
        self.connectCompletely = True
        self.encoding = 'utf-8'
        self.tcp_len = 64

    def send_message(self, message):
        message = message.encode(self.encoding)
        msg_len = len(message)
        msg_len = str(msg_len).encode(self.encoding)
        msg_len += b' ' * (self.tcp_len - len(msg_len))
        self.node.send(msg_len)
        self.node.send(message)

    def receive_message(self):
        m_len = int(self.node.recv(self.tcp_len).decode(self.encoding))
        data = self.node.recv(m_len).decode(self.encoding)
        return data

    def subscribe(self, message, topic):
        tic = time.time()
        self.send_message(message)
        data = self.receive_message()
        toc = time.time()
        if data == "subAck":
            if toc - tic < 10:
                print("subscribing on ", topic)
            else:
                print("subscribing failed.", topic)
                message = "disconnect"
                self.send_message(message)
                self.connectCompletely = False
        return

    def main(self):
        while self.connect:
            if sys.argv[4] == "publish":
                message = sys.argv[4] + ">" + sys.argv[5] + ">" + sys.argv[6]
                tic = time.time()
                self.send_message(message)
                data = self.receive_message()
                toc = time.time()
                if data == "pubAck":
                    if toc - tic > 10:
                        print("your message publishing failed")
                    else:
                        print("your message published successfully.")
                self.connect = False
            if sys.argv[4] == "subscribe":
                input_args = sys.argv
                for i in input_args[5:]:
                    message = "subscribe>" + i
                    # threading.Thread(target=self.subscribe, args=(message, i)).start()
                    self.subscribe(message, i)
                    self.connect = False

        self.connect = True
        while self.connect and self.connectCompletely:
            data = self.receive_message()
            print(data)
            if data == "ping":
                self.send_message("pong")
            if data == "disconnect":
                break


Client = ClientNode()
Client.main()
