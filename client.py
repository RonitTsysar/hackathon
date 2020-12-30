import socket
import time
from curtsies import Input
from threading import Thread
import struct
import sys
import colors


class Client():
    Port = 13117

    def __init__(self, name):
        # UDP
        self.conn_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # self.conn_udp.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)

        # struct format of messages
        self.udp_format = 'Ibh'
        self.magicCookie = 0xfeedbeef
        self.message_type = 0x2

        # Enable broadcasting mode
        # self.conn_udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.conn_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.conn_udp.bind(("", Client.Port))

        # TCP
        # self.conn_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.is_palying = False
        self.name = name

    def connect_tcp(self, ip, port):
        self.conn_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn_tcp.connect((ip, port))

    def close(self):
        self.conn_tcp.close()
        self.conn_tcp = None

    def looking_for_server(self):
        print(f"{colors.Yellow}Client started, listening for offer requests...{colors.Reset}")
        data, addr = None, None
        while True:
            data, addr = self.conn_udp.recvfrom(1024)
            # receive only udp messages of the format
            try:
                message = struct.unpack(self.udp_format, data)
            except struct.error:
                return
            if message[0] == self.magicCookie and message[1] == self.message_type:
                print(f"Received offer from {addr[0]}, attempting to connect...")
                break
        self.connecting_to_server(addr[0], int(message[2]))

    def connecting_to_server(self, ip, port):
        try:
            # TODO - fix that
            time.sleep(1)
            self.connect_tcp(ip, port)
        except Exception as e:
            print(f" connection failed , reconnecting ...")
            self.is_palying = False
            return

        # message = "RonitGal"
        self.conn_tcp.send(self.name.encode('utf-8'))
        self.is_palying = True


    def game_mode(self):
        with Input(keynames="curtsies", sigint_event=True) as input_generator:
            # try:
            while self.is_palying:
                key = input_generator.send(0.1)
                if key:
                    print(key)
                    self.conn_tcp.send((key + '\n').encode('utf-8'))
            # except Exception:
            #     return

    def recv_msgs(self):
        while True:
            try:
                message = self.conn_tcp.recv(1024)
            except:
                print("Server disconnected, listening for offer requestes...")
                self.is_palying = False
                return
            if not message:
                print("Server disconnected, listening for offer requestes...")
                self.is_palying = False
                return
            print(message.decode())


if __name__ == "__main__":
    name = str(sys.argv[1])

    client = Client(name)
    while True:
        client.looking_for_server()

        if client.is_palying:
            t1 = Thread(target=client.game_mode, daemon=True)
            t2 = Thread(target=client.recv_msgs, daemon=True)

            t1.start()
            t2.start()

            t1.join()
            t2.join()

            client.close()
