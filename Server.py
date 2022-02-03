import socket
import time
import threading


class ServerNode:

    def __init__(self):
        self.list_of_clients = []
        self.topics_dict = dict()
        self.encoding = 'utf-8'
        self.tcp_len = 64
        self.PORT = 1373
        self.HOST = '127.0.0.1'
        self.accept_connections()

    def accept_connections(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.server_socket:
            print("Server is on.")
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.HOST, self.PORT))
            self.server_socket.listen(100)
            print(f"Server is listening on port {self.PORT}")
            while True:
                conn, address = self.server_socket.accept()
                self.list_of_clients.append(conn)
                threading.Thread(target=self.handler, args=(conn, address)).start()

    def send_message(self, message, connection):
        message = message.encode(self.encoding)
        msg_len = len(message)
        msg_len = str(msg_len).encode(self.encoding)
        msg_len += b' ' * (self.tcp_len - len(msg_len))
        connection.send(msg_len)
        connection.send(message)

    def receive_message(self, connection):
        m_len = int(connection.recv(self.tcp_len).decode(self.encoding))
        data = connection.recv(m_len).decode(self.encoding)
        print(data)
        data_list = data.split(">")
        return data, data_list

    def publish(self, topic):
        if topic in self.topics_dict.keys():
            print("topic was already in the dictionary")
            return
        else:
            new_topic = {topic: []}
            self.topics_dict.update(new_topic)
            print("New topic with the concept of " + topic + " added.")

    def send_pub_ack(self, connection):
        pub_ack_msg = "pubAck"
        self.send_message(pub_ack_msg, connection)

    def broadcast(self, topic, topic_msg, conn):
        subscribed_clients = None
        message = topic + ": " + topic_msg
        print(message)
        if self.topics_dict[topic] is not None:
            for topic_key in self.topics_dict.keys():
                if topic_key == topic:
                    subscribed_clients = self.topics_dict[topic]
                    break
            for connection in subscribed_clients:
                if connection != conn:
                    print("sent to ", connection)
                    self.send_message(message, connection)

    def subscribe(self, conn, topic):
        if topic in self.topics_dict.keys():
            new_conns = self.topics_dict[topic]
            new_conns.append(conn)
            new_topic = {topic: new_conns}
            self.topics_dict.update(new_topic)
        else:
            new_topic = {topic: []}
            self.topics_dict.update(new_topic)
            print("New topic with the concept of " + topic + " added.")

    def send_sub_ack(self, connection):
        message = "subAck"
        self.send_message(message, connection)

    def handler(self, conn, address):
        with conn:
            ping_count = 0
            connect = True
            print("Connected by", address)
            while connect:
                data, data_list = self.receive_message(conn)
                if not data:
                    break
                if data == "disconnect":
                    break
                if data_list[0] == "publish":
                    self.send_pub_ack(conn)
                    self.publish(data_list[1])
                    self.broadcast(data_list[1], data_list[2], conn)
                    start_time = time.time()
                    while True:
                        self.send_message("ping", conn)
                        m_len = int(conn.recv(self.tcp_len).decode(self.encoding))
                        data = conn.recv(m_len).decode(self.encoding)
                        print(data)
                        if data != "pong":
                            print(address)
                            ping_count = ping_count + 1
                            if ping_count > 2:
                                connect = False
                                break
                        time.sleep(10.0 - ((time.time() - start_time) % 10.0))

                if data_list[0] == "subscribe":
                    self.send_sub_ack(conn)
                    self.subscribe(conn, data_list[1])
                    start_time = time.time()
                    while True:
                        self.send_message("ping", conn)
                        m_len = int(conn.recv(self.tcp_len).decode(self.encoding))
                        data = conn.recv(m_len).decode(self.encoding)
                        print(data)
                        if data != "pong":
                            print(address)
                            ping_count = ping_count + 1
                            if ping_count > 2:
                                connect = False
                                self.send_message("disconnect", conn)
                                break
                        time.sleep(10.0 - ((time.time() - start_time) % 10.0))

                else:
                    self.send_message("You entered wrong request", conn)
            self.remove_client(conn)
            print("Disconnected by", address)

    def remove_client(self, conn):
        self.list_of_clients.remove(conn)
        for topic_key in self.topics_dict.keys():
            if conn in self.topics_dict[topic_key]:
                self.topics_dict[topic_key].remove(conn)
                new_topic = {topic_key: self.topics_dict[topic_key]}
                self.topics_dict.update(new_topic)


server = ServerNode()
