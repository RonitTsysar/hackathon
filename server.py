import socket
import time
import random
from threading import Thread
from atomicInt import AtomicInteger


class Server():
    Port = 13117

    def __init__(self):
        # UDP
        self.conn_udp = socket.socket(socket.AF_INET,
                                      socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # Enable broadcasting mode
        self.conn_udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.ip = self.conn_udp.getsockname()[0]
        # TCP
        self.conn_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_ip = '172.18.0.67'
        server_address = (self.tcp_ip, Server.Port)
        self.conn_tcp.bind(server_address)

        self.is_broadcasting = True
        self.is_palying = True
        # check if need synchronized dict
        self.game_groups = {}
        self.group_1 = []
        self.group_2 = []
        self.group_A_counter = AtomicInteger()
        self.group_B_counter = AtomicInteger()

    # def close(self):
    #     self.conn.close()

    def broadcasting(self):
        message = f"Server started, listening on IP address {self.ip}"
        while self.is_broadcasting:
            self.conn_udp.sendto(message.encode('utf-8'),
                                 ('<broadcast>', Server.Port))
            time.sleep(1)

    def handle_clients(self, conn, ip, port):
        print('Connected by', self.tcp_ip)
        group_name = conn.recv(1024).decode()
        self.game_groups[group_name] = [conn, ip, port]

    def waiting_for_clients(self):
        # timeout for listening
        self.conn_tcp.settimeout(10)
        self.conn_tcp.listen()
        while True:
            try:
                (conn, (ip, port)) = self.conn_tcp.accept()
                Thread(target=self.handle_clients,
                       args=(conn, ip, port)).start()

            except socket.timeout:
                self.is_broadcasting = False
                break

    def game_mode(self):
        self.assign_random_groups()

    def finish_game(self):
        a = self.group_A_counter.value
        b = self.group_B_counter.value

        print("Game over!")
        print(f'''Group 1 typed in {a} characters.Group 2 typed in {b} characters.''')
        if(a > b):
            print('Group 1 wins!\nCongratulations to the winners:\n==')
            for group in self.group_1:
                print(group)
        elif(b > a):
            print('Group 2 wins!\nCongratulations to the winners:\n==')
            for group in self.group_2:
                print(group)
        else:
            print('its a tie\nCongratulations to the winners')

    def handle_group_A_game(self, group_name):
        conn = self.game_groups[group_name][0]
        while self.is_palying:
            data = conn.recv(1024).decode("utf-8").rstrip()
            self.group_A_counter.inc()
        print(self.group_A_counter.value)

    def handle_group_B_game(self, group_name):
        conn = self.game_groups[group_name][0]
        while self.is_palying:
            data = conn.recv(1024).decode("utf-8").rstrip()
            self.group_B_counter.inc()
        print(self.group_B_counter.value)

    def assign_random_groups(self):
        conns = []

        half_of_groups = int(len(self.game_groups)/2)
        all_groups = list(self.game_groups.keys())
        indices_to_choose = [i for i in range(len(self.game_groups))]

        for i in range(half_of_groups):
            chosen_idx = random.randint(0, len(indices_to_choose)-1)
            indices_to_choose.remove(indices_to_choose[chosen_idx])

            group_name = all_groups[indices_to_choose[chosen_idx]]
            self.group_1.append(group_name)
            conns.append(self.game_groups[group_name][0])
            Thread(target=self.handle_group_A_game, args=(group_name,)).start()

        for i in range(len(all_groups)):
            group_name = all_groups[i]
            self.group_2.append(group_name)
            conns.append(self.game_groups[group_name][0])
            Thread(target=self.handle_group_B_game, args=(group_name,)).start()

        # prepering the opening message
        opening_message = 'Welcome to Keyboard Spamming Battle Royal.\nGroup 1:\n==\n'
        for group in self.group_1:
            opening_message += group + '\n'
        opening_message += 'group 2:\n==\n'
        for group in self.group_2:
            opening_message += group + '\n'
        opening_message += 'Start pressing keys on your keyboard as fast as you can!!'

        # sending opening message to all clients
        for conn in conns:
            conn.send(opening_message.encode('utf-8'))

    def serve(self):
        # while True:
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

        # cleaning for another game


if __name__ == "__main__":

    server = Server()
    server.serve()
