import threading
import sys
import json
from connections.server import Server
from connections.client import Client

class View(threading.Thread):
    def __init__(self):
        super().__init__()

        with open("./setup/config.json", "r") as f:
            configs_file = json.load(f)

        self.server = Server((configs_file["central_server"]["host"],
                        configs_file["central_server"]["port"]))
                        
        self.client = Client([(configs_file["pisos"][floor_num]["host"],
                        configs_file["pisos"][floor_num]["port"]) for floor_num in range(3)])

    def run(self):
        # Inicia o servidor para ficar ouvindo mensagens dos andares
        self.server.start()              
        try:
            while True:             
                print("1 - Ativar Sinal de Lotado Estacionamento")
                print("2 - Desativar Sinal de Lotado Estacionamento")

                print("3 - Ativar Sinal de Lotado 1º Andar")
                print("4 - Desativar Sinal de Lotado 1º Andar")

                print("5 - Ativar Sinal de Lotado 2º Andar")
                print("6 - Desativar Sinal de Lotado 2º Andar\n")

                option = input()

                if option == '1':
                    data = {"msg": "ACTIVATE_FULL_SIGNAL"}
                    self.client.send_message(data, 0)
                elif option == '2':
                    data = {"msg": "DEACTIVATE_FULL_SIGNAL"}
                    self.client.send_message(data, 0)
                elif option == '3':
                    data = {"msg": "ACTIVATE_FULL_SIGNAL"}
                    self.client.send_message(data, 1)
                elif option == '4':
                    data = {"msg": "DEACTIVATE_FULL_SIGNAL"}
                    self.client.send_message(data, 1)
                elif option == '5':
                    data = {"msg": "ACTIVATE_FULL_SIGNAL"}
                    self.client.send_message(data, 2)
                elif option == '6':
                    data = {"msg": "DEACTIVATE_FULL_SIGNAL"}
                    self.client.send_message(data, 2)
                else:
                    print("Escolha uma opção válida!")

                print('\n')
        except KeyboardInterrupt:   
            print("Desligando Servidor Central ...")
            self.server.server_socket.close()
            sys.exit(0)