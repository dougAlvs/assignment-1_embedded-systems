import socket
import threading
import sys
from controller.message_handler import MessageHandler


class Server(threading.Thread):
    def __init__(self, server_address):
        super().__init__()

        self.server_address = server_address
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(server_address)
        self.message_handler = MessageHandler()

    def run(self):
        self.server_socket.listen()
        while True: 
            try:
                conn, addr = self.server_socket.accept()

                with conn:
                    # print(f"Connection established with: {addr}")

                    data = conn.recv(1024).decode("utf-8")

                    if not data:
                        print("Empty message!")
                        break
                    
                    try:
                        self.message_handler.process_msg(data)
                    except Exception as e:
                        print(f"Error processing message: {e}")
                        break

            except Exception as e:
                print(f"Error connecting with client: {e}")