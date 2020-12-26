from socket import *

class client():
    Port = 13117

    def __init__(self):
        self.conn = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        self.conn.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        
        # Enable broadcasting mode
        self.conn.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.conn.bind(("", client.Port))
    
    def close(self):
        self.conn.close()

    def lookingForServer(self):
        print("Client started, listening for offer requests...")
        data, addr = None, None
        while True:
            data, addr = self.conn.recvfrom(1024)
            print(f"Received offer from {addr[0]}, attempting to connect...")
            break
        print(f"addr {addr} ")

if __name__ == "__main__":
    client = client()
    client.lookingForServer()