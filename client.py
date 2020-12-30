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
        # UDP Socket
        self.conn_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        # struct format of messages
        self.udp_format = 'IbH'
        self.magicCookie = 0xfeedbeef
        self.message_type = 0x2

        # Enable broadcasting mode
        self.conn_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.conn_udp.bind(("", Client.Port))

        # variable that helps to determine if the client is still playing or not, updated accordingly.
        self.is_palying = False
        # name of client's team for the game
        self.name = name

    # initializes TCP connection with server in every game session
    def connect_tcp(self, ip, port):
        self.conn_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn_tcp.connect((ip, port))

    # closes TCP connection with server in every game session
    def close(self):
        self.conn_tcp.close()
        self.conn_tcp = None

    # looking for a server mode
    # receiving UDP broadcast messages from servers in order to initiate TCP connection with the first server
    def looking_for_server(self):
        print(f"{colors.Yellow}Client started, listening for offer requests...{colors.Reset}")
        data, addr = None, None
        while True:
            data, addr = self.conn_udp.recvfrom(1024)
            try:
                # receive only udp messages of the format
                message = struct.unpack(self.udp_format, data)
            except struct.error:
                return
            if message[0] == self.magicCookie and message[1] == self.message_type:
                print(f"Received offer from {addr[0]}, attempting to connect...")
                break
        # server's ip - add[0]
        # server's port - message[2]
        self.connecting_to_server(addr[0], int(message[2]))

    # try to connect the server with UDP conn in order to participate in the game
    def connecting_to_server(self, ip, port):
        try:
            time.sleep(1)
            self.connect_tcp(ip, port)
        except Exception as e:
            print(f" connection failed , reconnecting ...")
            # if connection is failed changes the variable is_playing
            self.is_palying = False
            return
        # send client name's team for the game
        self.conn_tcp.send(self.name.encode('utf-8'))
        self.is_palying = True

    # game mode - any key press event is caught and sent to the server
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

    # at game mode - recieving messages from the server
    # summary messages (game over and more...)
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
    # name of client entered by the user at running time
    name = str(sys.argv[1])

    client = Client(name)

    # Client runs "forever"
    while True:
        client.looking_for_server()

        # game mode!
        if client.is_palying:
            t1 = Thread(target=client.game_mode, daemon=True)
            t2 = Thread(target=client.recv_msgs, daemon=True)

            t1.start()
            t2.start()

            t1.join()
            t2.join()

            client.close()
