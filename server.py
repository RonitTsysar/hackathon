from socket import *
from threading import Thread
import time
import random

class Server():
    Port = 13117

    def __init__(self):
        #UDP
        self.conn_udp = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        # Enable broadcasting mode
        self.conn_udp.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.ip = self.conn_udp.getsockname()[0]
        #TCP
        self.conn_tcp = socket(AF_INET, SOCK_STREAM)
        # server_address = (self.ip, Server.Port)
        self.tcp_ip = '172.18.0.67'
        server_address = (self.tcp_ip, Server.Port)
        self.conn_tcp.bind(server_address)

        self.is_broadcasting = True
        # check if need synchronized dict
        self.game_groups = {}
        self.group_1 = {}
        self.group_2 = {}

    # def close(self):
    #     self.conn.close()

    def broadcasting(self):
        message = f"Server started, listening on IP address {self.ip}"
        while self.is_broadcasting:
            self.conn_udp.sendto(message.encode('utf-8'), ('<broadcast>', Server.Port))
            time.sleep(1)

    def handle_clients(self, conn, ip, port):
        # print('Connected by', self.ip)
        print('Connected by', self.tcp_ip)
        group_name = conn.recv(1024).decode()
        self.game_groups[group_name] = [conn, ip, port]

    def waiting_for_clients(self):
        self.conn_tcp.settimeout(10) # timeout for listening
        self.conn_tcp.listen()
        while True:
            try: 
                (conn, (ip, port)) = self.conn_tcp.accept()
                Thread(target=self.handle_clients, args=(conn, ip, port)).start()
                
            except timeout:
                self.is_broadcasting = False
                break

    def game_mode(self):
        # randomly assiging clients to 2 groups
        self.assign_random_groups()

        # open thread game for each client
        for client, conn_details in self.game_groups.items():
            Thread(target=self.handle_game_per_client, args=(conn_details,)).start()


    def assign_random_groups(self):
        half_of_groups  = int(len(self.game_groups)/2)
        all_groups = list(self.game_groups.keys())
        indices_to_choose = [i for i in range(len(self.game_groups))]
        random_chosen_indices = []

        for i in range(half_of_groups):
            chosen_idx = random.randint(0, len(indices_to_choose)-1)
            random_chosen_indices.append(indices_to_choose[chosen_idx])
            indices_to_choose.remove(indices_to_choose[chosen_idx])

        for i in range(len(all_groups)):
            group_name = all_groups[i]
            if i in random_chosen_indices:
                self.group_1[group_name] = self.game_groups[group_name]
                self.group_1[group_name].append(1)
            else:
                self.group_2[group_name] = self.game_groups[group_name]
                self.group_2[group_name].append(2)

    def handle_game_per_client(self, client_conn):
        conn = client_conn[0]
        opening_message = 'Welcome to Keyboard Spamming Battle Royal.\nGroup 1:\n==\n'

        for group in self.group_1:
            opening_message += group + '\n'

        opening_message += 'group 2:\n==\n'

        for group in self.group_2:
            opening_message += group + '\n'

        opening_message += 'Start pressing keys on your keyboard as fast as you can!!'

        conn.send(opening_message.encode('utf-8'))

        


    def serve(self):
        #while True:
        t1 = Thread(target=self.broadcasting, daemon=True)
        t2 = Thread(target=self.waiting_for_clients, daemon=True)
        
        t1.start()
        t2.start()

        t1.join()
        t2.join()

        self.game_mode()


if __name__ == "__main__":
    # game_groups = {'0':['d'], '1':['dsfs'], '2':['sdf'], '3':['dd'], '4':['sd'], '5':['awd'], '6':['sdf'], '7':['k'], '8':['resrt']}
    # group_1 = {}
    # group_2 = {}

    # half_of_groups  = int(len(game_groups)/2)
    # all_groups = list(game_groups.keys())
    # indices_to_choose = [i for i in range(len(game_groups))]
    # random_chosen_indices = []

    # for i in range(half_of_groups):
    #     chosen_idx = random.randint(0, len(indices_to_choose)-1)
    #     print(chosen_idx)
    #     random_chosen_indices.append(indices_to_choose[chosen_idx])
    #     print(random_chosen_indices)
    #     indices_to_choose.remove(indices_to_choose[chosen_idx])
    #     print(indices_to_choose)


    # for i in range(len(all_groups)):
    #     group_name = all_groups[i]
    #     if i in random_chosen_indices:
    #         group_1[group_name] = game_groups[group_name]
    #         group_1[group_name].append(1)
    #     else:
    #         group_2[group_name] = game_groups[group_name]
    #         group_2[group_name].append(2)

    # print(group_1)

    # print('##################')

    # print(group_2)
  

    server = Server()
    server.serve()


    # timeout = 10   # [seconds]
    # timeout_start = time.time()
    # while time.time() < timeout_start + timeout:
    #     server.sendto(message.encode('utf-8'), ('<broadcast>', Port))
    #     time.sleep(1)