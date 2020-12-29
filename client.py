import socket
import time
from curtsies import Input


class Client():
    Port = 13117

    def __init__(self):
        # UDP
        self.conn_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # self.conn_udp.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)

        # Enable broadcasting mode
        self.conn_udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.conn_udp.bind(("", Client.Port))

        # TCP
        self.conn_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # def close(self):
    #     self.conn.close()

    def looking_for_server(self):
        print("Client started, listening for offer requests...")
        data, addr = None, None
        while True:
            data, addr = self.conn_udp.recvfrom(1024)
            print(f"Received offer from {addr}, attempting to connect...")
            break
        self.connecting_to_server(addr[0])

    def connecting_to_server(self, ip):
        time.sleep(1)
        self.conn_tcp.connect((ip, Client.Port))
        message = "RonitGal"
        self.conn_tcp.send(message.encode('utf-8'))

    def game_mode(self):
        opening_message = self.conn_tcp.recv(1024).decode()
        print(opening_message)

        with Input(keynames='curtsies') as input_generator:
            for e in input_generator:
                self.conn_tcp.send((e + '\n').encode('utf-8'))
                print(e)


if __name__ == "__main__":
    client = Client()
    client.looking_for_server()
    client.game_mode()
