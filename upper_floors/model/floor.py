import json
import threading
import RPi.GPIO as GPIO
import time
from connections.client import Client

class Floor(threading.Thread):
    def __init__(self, floor_num):
        super().__init__()
        self.floor_num = floor_num
        self.floors_names = ['Térreo', 'Primeiro Andar', 'Segundo Andar']

        with open("./setup/config.json", "r") as f:
            configs_file = json.load(f)

        outputs = configs_file["pisos"][floor_num]["outputs"]
        inputs = configs_file["pisos"][floor_num]["inputs"]
        
        self.local_server_address = (configs_file["pisos"][self.floor_num]["host"],
                        configs_file["pisos"][self.floor_num]["port"])

        self.client = Client((configs_file["central_server"]["host"],
                        configs_file["central_server"]["port"]))

        for out in outputs:
            if out["tag"] == "ENDERECO_01":
                self.addr_1 = out["gpio"]
            elif out["tag"] == "ENDERECO_02":
                self.addr_2 = out["gpio"]
            elif out["tag"] == "ENDERECO_03":
                self.addr_3 = out["gpio"]
            elif out["tag"] == "SINAL_DE_LOTADO_FECHADO":
                self.led_full = out["gpio"]

        for inp in inputs:
            if inp["tag"] == "SENSOR_DE_VAGA":
                self.spot_sensor = inp["gpio"]
            elif inp["tag"] == "SENSOR_DE_PASSAGEM_1":
                self.pass_sensor_1 = inp["gpio"]
            elif inp["tag"] == "SENSOR_DE_PASSAGEM_2":
                self.pass_sensor_2 = inp["gpio"]


        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        GPIO.setup(self.pass_sensor_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.pass_sensor_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        self.sensors_order = []

        # Sinal de Lotado - Led
        GPIO.setup(self.led_full, GPIO.OUT)

        # Sensores de Vagas       
        GPIO.setup(self.addr_1, GPIO.OUT)
        GPIO.setup(self.addr_2, GPIO.OUT)
        GPIO.setup(self.addr_3, GPIO.OUT)
        GPIO.setup(self.spot_sensor, GPIO.IN)
        
        # Define os valores das vagas
        self.output_values = [[GPIO.LOW, GPIO.LOW, GPIO.LOW],    # 0
                            [GPIO.LOW, GPIO.LOW, GPIO.HIGH],     # 1
                            [GPIO.LOW, GPIO.HIGH, GPIO.LOW],     # 2
                            [GPIO.LOW, GPIO.HIGH, GPIO.HIGH],    # 3
                            [GPIO.HIGH, GPIO.LOW, GPIO.LOW],     # 4
                            [GPIO.HIGH, GPIO.LOW, GPIO.HIGH],    # 5
                            [GPIO.HIGH, GPIO.HIGH, GPIO.LOW],    # 6
                            [GPIO.HIGH, GPIO.HIGH, GPIO.HIGH]]   # 7
        
        self.spots_state = [0 for _ in range(8)]

    def change_led_full_state(self, state):
        if state:
            GPIO.output(self.led_full, GPIO.HIGH)
        else:
            GPIO.output(self.led_full, GPIO.LOW)

    def check_passage_sensors_state(self, channel):
        if GPIO.input(self.pass_sensor_1):
            self.sensors_order.append(1)
        elif GPIO.input(self.pass_sensor_2):
            self.sensors_order.append(2)

    def check_car_passage_direction(self):
        while True:
            if len(self.sensors_order) == 2:
                if self.sensors_order == [1, 2]:
                    print(f"Carro subindo do {self.floors_names[self.floor_num - 1]} para o {self.floors_names[self.floor_num]}.\n")
                    data = {"msg": "CAR_MOVING_FLOORS", "from": self.floor_num - 1, "to": self.floor_num, "sender_floor_id": self.floor_num}
                    self.client.send_message(data)
                elif self.sensors_order == [2, 1]:
                    print(f"Carro descendo do {self.floors_names[self.floor_num]} para o {self.floors_names[self.floor_num - 1]}.\n")
                    data = {"msg": "CAR_MOVING_FLOORS", "from": self.floor_num, "to": self.floor_num - 1, "sender_floor_id": self.floor_num}
                    self.client.send_message(data)
                self.sensors_order = []

            time.sleep(0.5)

    def check_parking_spots_state(self):
        while True:
            for i, output_value in enumerate(self.output_values):
                # Configura os pinos para a vaga atual
                GPIO.output(self.addr_3, output_value[0])
                GPIO.output(self.addr_2, output_value[1])
                GPIO.output(self.addr_1, output_value[2])

                time.sleep(0.05)

                # Caso algum carro ocupe alguma vaga
                if GPIO.input(self.spot_sensor) and not self.spots_state[i]:
                    self.spots_state[i] = 1
                    print(f"Vaga {i} foi ocupada.\n")
                    data = {"msg": "CAR_PARKING", "parking_spot_id": i, "sender_floor_id": self.floor_num}
                    self.client.send_message(data)

                # Caso algum carro libere alguma vaga
                elif not GPIO.input(self.spot_sensor) and self.spots_state[i]:
                    self.spots_state[i] = 0
                    print(f"Vaga {i} foi desocupada.\n")
                    data = {"msg": "CAR_LEAVING_SPOT", "parking_spot_id": i, "sender_floor_id": self.floor_num}
                    self.client.send_message(data)

                time.sleep(0.05)

            time.sleep(0.5)

    def run(self):
        GPIO.add_event_detect(self.pass_sensor_1, GPIO.BOTH, callback=self.check_passage_sensors_state)
        GPIO.add_event_detect(self.pass_sensor_2, GPIO.BOTH, callback=self.check_passage_sensors_state)

        # Thread para checar periodicamente as vagas
        spot_thread = threading.Thread(target=self.check_parking_spots_state)
        spot_thread.daemon = True
        spot_thread.start()

        # Thread para checar periodicamente os sensores de passagem
        passage_sensor_thread = threading.Thread(target=self.check_car_passage_direction)
        passage_sensor_thread.daemon = True
        passage_sensor_thread.start()

        spot_thread.join()
        passage_sensor_thread.start()