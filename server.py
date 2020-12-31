import socket
import time
import random
import colors
from threading import Thread
from atomicInt import AtomicInteger
from struct import pack
from scapy.arch import get_if_addr


class Server():
    UDP_PORT = 13117
    TCP_PORT = 1818

    def __init__(self):
        self.conn_udp = socket.socket(socket.AF_INET,
                                      socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # struct format of messages
        self.udp_format = 'IbH'
        self.magicCookie = 0xfeedbeef
        self.message_type = 0x2

        # Enable broadcasting mode
        self.conn_udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        self.conn_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_ip = get_if_addr('eth1')

        server_address = (self.tcp_ip, Server.TCP_PORT)
        self.conn_tcp.bind(server_address)

        self.is_broadcasting = True
        self.is_palying = True
        self.game_groups = {}
        self.tcp_conns = []
        self.group_1 = []
        self.group_2 = []
        self.group_A_counter = AtomicInteger()
        self.group_B_counter = AtomicInteger()

    # broadcasting UDP message, 1 every 1 second
    def broadcasting(self):
        print(f"{colors.Magenta}Server started, listening on IP address {self.tcp_ip}{colors.Reset}")

        message = pack(self.udp_format, self.magicCookie, self.message_type, Server.TCP_PORT)
        while self.is_broadcasting:
            self.conn_udp.sendto(message,
                                 ('172.1.255.255', Server.UDP_PORT))
            time.sleep(1)

    def handle_clients(self, conn, ip, port):
        group_name = conn.recv(1024).decode()
        print(f"{colors.Bright_Magenta}     {group_name} connected with {self.tcp_ip} ip {colors.Reset} ")

        self.game_groups[group_name] = [conn, ip, port]
        # collecting clients connections
        self.tcp_conns.append(conn)

    # waiting for cilent to connect over TCP.
    def waiting_for_clients(self):
        # TCP soclet listen only for 10 seconds
        self.conn_tcp.settimeout(10)
        self.conn_tcp.listen()
        while True:
            try:
                # each client handle in separate thread
                (conn, (ip, port)) = self.conn_tcp.accept()
                Thread(target=self.handle_clients,
                       args=(conn, ip, port), daemon=True).start()

            except socket.timeout:
                self.is_broadcasting = False
                break
    
    # executed 10 seconds
    def game_mode(self):
        self.assign_random_groups()

    def finish_game(self):
        a = self.group_A_counter.value
        b = self.group_B_counter.value

        # prepering the summary message
        summary_message = f'{colors.Bright_Cyan}Game over!{colors.Reset}\nGroup 1 typed in ' + str(a) + ' characters. Group 2 typed in ' + str(b) + ' characters.\n'
        if(a > b):
            summary_message += 'Group 1 wins!\nCongratulations to the winners:\n==\n'
            for group in self.group_1:
                summary_message += group + '\n'

        elif(b > a):
            summary_message += f'Group 2 wins!\n{colors.Bright_Cyan}Congratulations to the winners:{colors.Reset}\n==\n'
            for group in self.group_2:
                summary_message += group + '\n'

        else:
            summary_message += 'its a tie!\nCongratulations to the winners.'

        # sending summary message to all clients
        for conn in self.tcp_conns:
            conn.send(summary_message.encode('utf-8'))

        # close all tcp slaves connections
        for conn in self.tcp_conns:
            try:
                conn.shutdown(socket.SHUT_RD)
                conn.close()
            except:
                pass

        self.clean_up()
        print(f"{colors.Yellow}========================================={colors.Reset}​")
        print(f"{colors.Magenta}Game over, sending out offer requests...{colors.Reset}​")
        print(f"{colors.Yellow}========================================={colors.Reset}​")

    def handle_group_A_game(self, group_name):
        conn = self.game_groups[group_name][0]
        # while playing receiving messages from the client and count them
        while self.is_palying:
            try:
                data = conn.recv(1024).decode("utf-8").rstrip()
                self.group_A_counter.inc()
            except Exception:
                pass

    def handle_group_B_game(self, group_name):
        conn = self.game_groups[group_name][0]
        # while playing receiving messages from the client and count them
        while self.is_palying:
            try:
                data = conn.recv(1024).decode("utf-8").rstrip()
                self.group_B_counter.inc()
            except Exception:
                pass

    def assign_random_groups(self):
        # no game if there are no clients
        if len(self.game_groups) < 1:
            print(f"{colors.Yellow}There are less then 1 client connected in this game.{colors.Reset}")
            return

        half_of_groups = int(len(self.game_groups)/2)
        all_groups = list(self.game_groups.keys())
        indices_to_choose = [i for i in range(len(self.game_groups))]

        self.is_palying = True

        # half of the quantity goes to group 1
        for i in range(half_of_groups):
            chosen_idx = random.randint(0, len(indices_to_choose)-1)
            group_name = all_groups[indices_to_choose[chosen_idx]]
            indices_to_choose.remove(indices_to_choose[chosen_idx])

            self.group_1.append(group_name)
            Thread(target=self.handle_group_A_game, args=(group_name,), daemon=True).start()
        
        # half of the quantity goes to group 2
        for i in range(len(indices_to_choose)):
            group_name = all_groups[indices_to_choose[i]]
            self.group_2.append(group_name)
            Thread(target=self.handle_group_B_game, args=(group_name,), daemon=True).start()

        # prepering the opening message
        opening_message = f'{colors.Bright_Cyan}Welcome to Keyboard Spamming Battle Royal.{colors.Reset}\n{colors.Bright_Cyan}Group 1:\n=={colors.Reset}\n'
        for group in self.group_1:
            opening_message += group + '\n'
        opening_message += f'{colors.Bright_Cyan}Group 2:\n=={colors.Reset}\n'
        for group in self.group_2:
            opening_message += group + '\n'
        opening_message += f'{colors.Bright_Cyan}Start pressing keys on your keyboard as fast as you can!!{colors.Reset}'

        # sending opening message to all clients
        for conn in self.tcp_conns:
            conn.send(opening_message.encode('utf-8'))

    # reset all the params to the initial value, before new "round"
    def clean_up(self):
        self.is_broadcasting = True

        self.game_groups = {}
        self.tcp_conns = []
        self.group_1 = []
        self.group_2 = []
        self.group_A_counter.value = 0
        self.group_B_counter.value = 0

    def serve(self):
        while True:
            t1 = Thread(target=self.broadcasting, daemon=True)
            t2 = Thread(target=self.waiting_for_clients, daemon=True)

            t1.start()
            t2.start()

            t1.join()
            t2.join()

            self.game_mode()

            time.sleep(10)
            self.is_palying = False

            self.finish_game()

if __name__ == "__main__":
    server = Server()
    server.serve()
