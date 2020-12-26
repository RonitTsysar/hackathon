from socket import *
import time

class Client():
    Port = 13117

    def __init__(self):
        #UDP
        self.conn_udp = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        self.conn_udp.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        
        # Enable broadcasting mode
        self.conn_udp.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.conn_udp.bind(("", Client.Port))

        #TCP
        self.conn_tcp = socket(AF_INET, SOCK_STREAM)

    def close(self):
        self.conn.close()

    def lookingForServer(self):
        print("Client started, listening for offer requests...")
        data, addr = None, None
        while True:
            data, addr = self.conn_udp.recvfrom(1024)
            print(f"Received offer from {addr}, attempting to connect...")
            break 
        self.connectingToServer(addr[0])
    
    def connectingToServer(self, ip):
        time.sleep(1)
        self.conn_tcp.connect((ip, Client.Port))
        message = "RonitGal"
        self.conn_tcp.send(message.encode('utf-8'))

if __name__ == "__main__":
    client = Client()
    client.lookingForServer()