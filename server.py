from socket import *
from threading import Thread
import time

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
        server_address = (self.ip, Server.Port)
        self.conn_tcp.bind(server_address)

        self.is_broadcasting = True

    # def close(self):
    #     self.conn.close()

    def broadcasting(self):
        message = f"Server started, listening on IP address {self.ip}"
        while self.is_broadcasting:
            self.conn_udp.sendto(message.encode('utf-8'), ('<broadcast>', Server.Port))
            time.sleep(1)

    def handle_clients(self, conn):
        print('Connected by', self.ip)
        data = conn.recv(1024)
        print(f" data {data} ")

    def waiting_for_clients(self):
        self.conn_tcp.settimeout(10) # timeout for listening
        self.conn_tcp.listen()
        print("------------------------------------------------")
        while True:
            try: 
                (conn, (ip, port)) = self.conn_tcp.accept()
                Thread(target=self.handle_clients, args=(conn,)).start()
                
            except timeout:
                self.is_broadcasting = False
                break

    def serve(self):
        #while True:
        t1 = Thread(target=self.broadcasting, daemon=True)
        t2 = Thread(target=self.waiting_for_clients, daemon=True)
        
        t1.start()
        t2.start()

        t1.join()
        t2.join()

        # self.waiting_for_clients()


if __name__ == "__main__":
    server = Server()
    server.serve()



    # timeout = 10   # [seconds]
    # timeout_start = time.time()
    # while time.time() < timeout_start + timeout:
    #     server.sendto(message.encode('utf-8'), ('<broadcast>', Port))
    #     time.sleep(1)
