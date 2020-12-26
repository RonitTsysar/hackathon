from socket import *
import time

class Server():
    IP = "172.18.0.67"
    Port = 13117

    def __init__(self):
        self.conn = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        # Enable broadcasting mode
        self.conn.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    
    def close(self):
        self.conn.close()

    def waiting_for_clients(self):
        message = f"Server started, listening on IP address {Server.IP}"
        #while True:
        for i in range(10):
            self.conn.sendto(message.encode('utf-8'), ('<broadcast>', Server.Port))
            time.sleep(1)
    
    def serve(self):
        while True:
            self.waiting_for_clients()

if __name__ == "__main__":
    server = Server()
    server.serve()



    


    # timeout = 10   # [seconds]
    # timeout_start = time.time()
    # while time.time() < timeout_start + timeout:
    #     server.sendto(message.encode('utf-8'), ('<broadcast>', Port))
    #     time.sleep(1)
