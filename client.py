import socket
import time
from curtsies import Input
from threading import Thread


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

    def close(self):
        self.conn_udp.close()
        self.conn_tcp.close()

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
        with Input(keynames="curtsies", sigint_event=True) as input_generator:
            try:
                while self.is_palying:
                    key = input_generator.send(0.1)
                    if key:
                        print(key)
                        self.conn_tcp.send((key + '\n').encode('utf-8'))
            except Exception:
                return

    def recv_msgs(self):
        while True:
            message = self.conn_tcp.recv(1024)
            if not message:
                print("----------- END -----------")
                self.is_palying = False
                return
            print(message.decode())


if __name__ == "__main__":
    client = Client()
    client.looking_for_server()

    client.is_palying = True
    t1 = Thread(target=client.game_mode, daemon=True)
    t2 = Thread(target=client.recv_msgs, daemon=True)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    client.close()
