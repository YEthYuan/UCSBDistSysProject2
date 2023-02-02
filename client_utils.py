import hashlib
import json
import yaml
import queue
import random
import socket

import sys
import threading
import time


class Client:
    def __init__(self, username: str, config_path="./config.yaml", sleep=0):
        self.username = username
        self.sleep = sleep
        self.config = self.load_config(config_path)

        self.user_list = {}
        self.in_channels = {}
        self.in_list = []
        self.out_channels = {}
        self.out_list = []
        self.addr = ()
        self.init_network(self.config)

        self.token = False
        self.lose_prob = 0  # percentage of the probability to lose the token


        pass

    def load_config(self, path: str) -> dict:
        with open(path, 'r') as file:
            config = yaml.load(file, Loader=yaml.FullLoader)

        print(f"==>Config file loaded from {path}!")
        # print(config)

        return config

    def message_delay(self):
        if self.sleep == -1:
            sleep_time = random.uniform(0, 3)
            time.sleep(sleep_time)
        elif self.sleep:
            time.sleep(self.sleep)

    def init_network(self, config: dict) -> None:
        for u in config['clients']:
            username = u['username']
            ip = u['ip']
            port = u['port']
            addr = (ip, port)
            self.user_list[username] = addr

        for es in config['edges']:
            if self.username == es['node']:
                self.addr = self.user_list[es['node']]
                for to in es['to']:
                    self.out_channels[to] = self.user_list[to]
                    self.out_list.append(to)
                for fr in es['from']:
                    self.in_channels[fr] = self.user_list[fr]
                    self.in_list.append(fr)

    def process_token(self, payload: dict):
        sender = payload['sender']
        self.token = True
        print(f"Client {self.username} holds the token now!")

        time.sleep(1)

        to = random.choice(self.out_list)
        self.send_token(to=to)

    def send_token(self, to: str):
        self.token = False
        print(f"Client {self.username} no longer holds the token!")
        payload = {
            "sender": self.username,
            "receiver": to
        }
        payload = json.dumps(payload)
        message = self.generate_packet_to_send(payload, "token")
        message = json.dumps(message)

        # client may lose the token
        R = random.randint(1, 100)
        if R <= self.lose_prob:
            print(f"!!!!!!!!!!!!!!!!!! The token is lost by {self.username} !!!!!!!!!!!!!!!!!!")
            return
        else:
            self.message_delay()

            addr = self.user_list[to]
            self.send_udp_packet(message, *addr)
            print(f"Token has been sent to user {to}!")

    def process_marker(self, payload: dict):
        pass

    def broadcast_marker(self, initiator: str):
        payload = {
            "initiator": initiator,
            "sender": self.username
        }
        payload = json.dumps(payload)
        message = self.generate_packet_to_send(payload, "marker")
        message = json.dumps(message)
        self.message_delay()

        for to_name, to_addr in self.out_channels.items():
            self.send_udp_packet(message, *to_addr)
            print(f"MARKER has been sent to user {to_name}!")

    def generate_packet_to_send(self, msg_item: str, msg_type: str) -> dict:
        """
        Packet definition:
        packet = {
            'type': [],
            'item': str (can be a dumped json string)
        }
        :param msg_item:
        :param msg_type:
        :return:
        """
        packet = {
            'type': msg_type,
            'item': msg_item,
            'from': self.username
        }
        return packet

    def send_udp_packet(self, data: str, host: str, port: int):
        """
        Sends a UDP packet to a specified host and port

        Args:
        data: str: the message you want to send
        host: str: the destination IP address
        port: int: the destination port

        Returns:
        None

        """
        # Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Send the packet
            sock.sendto(data.encode(), (host, port))
        finally:
            # Close the socket
            sock.close()

    def init_udp_recv_settings(self):
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.bind(self.my_addr)
        self.data_queue = queue.Queue()

    def start_listening(self):
        # Start the thread to listen for UDP packets
        self.udp_thread = threading.Thread(target=self.listen_for_udp)
        self.udp_thread.start()

    def listen_for_udp(self):
        while not self.stop_udp_thread:
            data, addr = self.udp_sock.recvfrom(1024)
            # print("Received data:", data)
            # print("From address:", addr)
            self.process_recv_data(data)

    def stop_udp(self):
        self.stop_udp_thread = True
        self.udp_thread.join()

    def process_recv_data(self, data):
        data = json.loads(data)
        if data['type'] == 'token':
            print(f"==>Received token from {data['from']}. ")
            payload = data['item']
            payload = json.loads(payload)
            self.process_token(payload)
        elif data['type'] == 'marker':
            print(f"==>Received MARKER from {data['from']}. ")
            payload = data['item']
            payload = json.loads(payload)
            self.process_marker(payload)
        elif data['type'] == 'client-release':
            pass
        elif data['type'] == 'server-balance':
            pass
        elif data['type'] == 'server-status':
            pass


if __name__ == '__main__':
    pass