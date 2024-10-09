import json
# from messages_codes import  *
from model.car import Car 
from model.floor import Floor
from connections.client import Client

class MessageHandler():
    def __init__(self):
        with open("./setup/config.json", "r") as f:
            configs_file = json.load(f)

        self.floors = [Floor(i) for i in range(3)]
        self.cars_num = 0

        self.client = Client([(configs_file["pisos"][floor_num]["host"],
                        configs_file["pisos"][floor_num]["port"]) for floor_num in range(3)])

    def process_msg(self, msg):
        try:
            json_msg = json.loads(msg)
        except json.JSONDecodeError as e:
            print(f"Invalid message format: {e}")
            return

        sender_floor = self.floors[json_msg["sender_floor_id"]]
        # print(f"Mensagem {json_msg['msg']} recebida do andar {sender_floor.floor_num}")

        if json_msg["msg"] == "CAR_ENTRANCE":
          self.process_car_entrance(sender_floor)

        if json_msg["msg"] == "CAR_MOVING_FLOORS":
          self.process_car_moving_floors(json_msg)

        elif json_msg["msg"] == "CAR_LEAVING_SPOT":
            self.process_car_leaving_spot(sender_floor, json_msg)

        elif json_msg["msg"] == "CAR_EXIT":
            self.process_car_exit(sender_floor)

        elif json_msg["msg"] == "CAR_PARKING":
             self.process_car_parking(sender_floor, json_msg)


    def show_cars_total(self):
        print(f"Total de carros no estacionamento: {self.cars_num}/24")
        print(f"Total de carros no térreo: {self.floors[0].cars_num}/8")
        print(f"Total de carros no primeiro andar: {self.floors[1].cars_num}/8")
        print(f"Total de carros no segundo andar: {self.floors[2].cars_num}/8\n")

    def show_spots_total(self, sender_floor):
        esp_num, elder_num, reg_num = sender_floor.check_occupied_spots()
        print(f"Total de vagas ocupadas no {sender_floor.floor_name}")
        print(f"Para portadores de necessidades especiais: {esp_num}/1")
        print(f"Para idosos: {elder_num}/2")
        print(f"Regulares: {reg_num}/5\n")

    def process_car_moving_floors(self, json_msg):
        moving_from_floor = self.floors[json_msg["from"]]
        moving_to_floor = self.floors[json_msg["to"]]

        # Atualiza a contagem de carros dos dois andares
        moving_from_floor.cars_num -= 1
        moving_to_floor.cars_num += 1

        if json_msg["from"] < json_msg["to"]:
            moving_to_floor.cars.append(moving_from_floor.cars.pop())

        self.show_cars_total()

    def process_car_entrance(self, sender_floor):
        sender_floor.cars.append(Car())
        self.cars_num += 1
        sender_floor.cars_num += 1

        self.show_cars_total()

    def process_car_exit(self, sender_floor):
        self.cars_num -= 1
        sender_floor.cars_num -= 1

        self.show_spots_total(sender_floor)

    def process_car_parking(self, sender_floor, json_msg):
        parking_spot_id = json_msg["parking_spot_id"]

        sender_floor.park_car(parking_spot_id)

        if sum(sender_floor.check_occupied_spots()) == 8:
            data = {"msg": "ACTIVATE_FULL_SIGNAL"}
            self.client.send_message(data, sender_floor.floor_num)
            print(f"{sender_floor.floor_name} lotado!")

        if self.cars_num == 24:
            data = {"msg": "ACTIVATE_FULL_SIGNAL"}
            self.client.send_message(data, 0)
            print(f"Estacionamento lotado!")

        self.show_spots_total(sender_floor)
        
    def process_car_leaving_spot(self, sender_floor, json_msg):
        occupied_spots_before = sum(sender_floor.check_occupied_spots())
        parking_spot_id = json_msg["parking_spot_id"]

        sender_floor.leave_car_spot(parking_spot_id)

        # Se o andar não estiver mais lotado, desliga o sinal de lotação
        if occupied_spots_before == 8:
            data = {"msg": "DEACTIVATE_FULL_SIGNAL"}
            self.client.send_message(data, sender_floor.floor_num)
            print(f"{sender_floor.floor_name} não está mais lotado!")

        self.show_spots_total(sender_floor)


