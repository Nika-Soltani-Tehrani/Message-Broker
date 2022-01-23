import socket
import threading


class ServerNode:

    def __init__(self):
        self.list_of_clients = []
        self.topics_dict = dict()
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

    @staticmethod
    def send_message(message, connection):
        connection.sendall(message.encode())

    @staticmethod
    def receive_message(connection):
        # while True:
        data = connection.recv(1024).decode()
        print(data)
        data_list = data.split(">")
        return data, data_list

    def publish(self, topic, conn):
        if topic in self.topics_dict.keys():
            self.send_pub_ack(conn)
            return
        else:
            new_topic = {topic: []}
            self.topics_dict.update(new_topic)
            print("New topic with the concept of " + topic + " added.")
            self.send_pub_ack(conn)

    def send_pub_ack(self, connection):
        pub_ack_msg = "your message published successfully"
        self.send_message(pub_ack_msg, connection)

    def broadcast(self, topic, topic_msg, conn):
        subscribed_clients = None
        message = topic + ": " + topic_msg
        # print(topic)
        # print(self.topics_dict[topic])
        if self.topics_dict[topic] is not None:
            for topic_key in self.topics_dict.keys():
                if topic_key == topic:
                    subscribed_clients = self.topics_dict[topic]
                    break
            for connection in subscribed_clients:
                if connection != conn:
                    connection.sendall(message.encode())

    def subscribe(self, conn, topic_list):
        successful_subscriptions = []
        failed_subscriptions = []
        for topic in topic_list:
            if topic in self.topics_dict.keys():
                new_conns = self.topics_dict[topic]
                new_conns.append(conn)
                new_topic = {topic: new_conns}
                self.topics_dict.update(new_topic)
                successful_subscriptions.append(topic)
            else:
                failed_subscriptions.append(topic)
            self.send_sub_ack(conn, successful_subscriptions, failed_subscriptions)

    def send_sub_ack(self, connection, successful_topic_list, failed_topic_list):
        p_sub_ack_msg = "subscribing on: "
        n_sub_ack_msg = "subscription failed for"
        message = p_sub_ack_msg, successful_topic_list, "and", n_sub_ack_msg, failed_topic_list
        self.send_message(message, connection)

    def handler(self, conn, address):
        with conn:
            print("Connected by", address)
            while True:
                data, data_list = self.receive_message(conn)
                if not data:
                    break
                if data == "disconnect":
                    break
                if data_list[2] == "publish":
                    self.publish(data_list[3], conn)
                    self.broadcast(data_list[3], data_list[4], conn)
                if data_list[2] == "subscribe":
                    self.subscribe(conn, data_list[3:])
                else:
                    self.send_message("You entered wrong request", conn)
            self.remove_client(conn)
            print("Disconnected by", address)

    def remove_client(self, conn):
        self.list_of_clients.remove(conn)


server = ServerNode()
