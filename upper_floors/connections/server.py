import socket
import threading
import time
import json
import sys

class Server(threading.Thread):
    def __init__(self, floor):
        super().__init__()

        with open("./setup/config.json", "r") as f:
            configs_file = json.load(f)

        self.floor = floor

        self.server_address = (configs_file["pisos"][self.floor.floor_num]["host"],
                        configs_file["pisos"][self.floor.floor_num]["port"])
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(self.server_address)

    def run(self):
        self.floor.start()
        self.server_socket.listen()
        try:
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
                            json_data = json.loads(data)
                        except json.JSONDecodeError as e:
                            print(f"Invalid message format: {e}")
                            return

                        if json_data["msg"] == "ACTIVATE_FULL_SIGNAL":
                            self.floor.change_led_full_state(True)
                        
                        if json_data["msg"] == "DEACTIVATE_FULL_SIGNAL":
                            self.floor.change_led_full_state(False)            

                        time.sleep(0.1)

                except Exception as e:
                    print(f"Error connecting with client: {e}")
                    time.sleep(0.5)
                    
        except KeyboardInterrupt:
            self.socket.close()
            print('Servidor Central desligado.')
            sys.exit(0)