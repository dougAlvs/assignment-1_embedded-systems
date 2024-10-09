import socket
import json

class Client:
    def __init__(self, address):
        self.central_server_address = address
    
    def send_message(self, data):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(self.central_server_address)
                s.sendall(json.dumps(data).encode("utf-8"))
                # print(f"Message sent successfully to central server")
        except Exception as e:
            print(f"Error sending message to central server: {e}")
