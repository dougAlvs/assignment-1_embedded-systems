import socket
import json

class Client:
    def __init__(self, clients_address):
        self.clients_address = clients_address
        self.num_clients = len(clients_address)
    
    def send_message(self, data, client_num):
        if client_num >= self.num_clients or client_num < 0:
            print(f"Client number {client_num} is invalid!")
            return
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(self.clients_address[client_num])
                s.sendall(json.dumps(data).encode("utf-8"))
                # print(f"Message sent successfully to server {client_num}")
        except Exception as e:
            print(f"Error server {client_num}: {e}")