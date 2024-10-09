import json
import threading
import RPi.GPIO as GPIO
import time
from connections.client import Client

class Floor(threading.Thread):
    def __init__(self):
        super().__init__()
        self.floor_num = 0

        with open("./setup/config.json", "r") as f:
            configs_file = json.load(f)

        outputs = configs_file["pisos"][self.floor_num]["outputs"]
        inputs = configs_file["pisos"][self.floor_num]["inputs"]
        
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
            elif out["tag"] == "MOTOR_CANCELA_ENTRADA":
                self.entrance_gate = out["gpio"]
            elif out["tag"] == "MOTOR_CANCELA_SAIDA":
                self.exit_gate = out["gpio"]

        for inp in inputs:
            if inp["tag"] == "SENSOR_DE_VAGA":
                self.spot_sensor = inp["gpio"]
            elif inp["tag"] == "SENSOR_ABERTURA_CANCELA_ENTRADA":
                self.entrance_opening_sensor = inp["gpio"]
            elif inp["tag"] == "SENSOR_FECHAMENTO_CANCELA_ENTRADA":
                self.entrance_closing_sensor = inp["gpio"]
            elif inp["tag"] == "SENSOR_ABERTURA_CANCELA_SAIDA":
                self.exit_opening_sensor = inp["gpio"]
            elif inp["tag"] == "SENSOR_FECHAMENTO_CANCELA_SAIDA":
                self.exit_closing_sensor = inp["gpio"]

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Cancela Entrada
        self.is_entrance_gate_open = False
        
        GPIO.setup(self.entrance_opening_sensor, GPIO.IN)
        GPIO.setup(self.entrance_closing_sensor, GPIO.IN)
        GPIO.setup(self.entrance_gate, GPIO.OUT) 

        GPIO.output(self.entrance_gate, GPIO.LOW) # inicia motor entrada em LOW

        # Cancela Saida
        self.is_exit_gate_open = False
        
        GPIO.setup(self.exit_opening_sensor, GPIO.IN)
        GPIO.setup(self.exit_closing_sensor, GPIO.IN)
        GPIO.setup(self.exit_gate, GPIO.OUT) 

        GPIO.output(self.exit_gate, GPIO.LOW) # inicia motor saida em LOW

        # Sinal de Lotado - Led
        GPIO.setup(self.led_full, GPIO.OUT)

        # Sensores de Vagas       
        GPIO.setup(self.addr_1, GPIO.OUT)
        GPIO.setup(self.addr_2, GPIO.OUT)
        GPIO.setup(self.addr_3, GPIO.OUT)
        GPIO.setup(self.spot_sensor, GPIO.IN)
        
        # Define os valores das vagas
        self.output_values = [[GPIO.LOW, GPIO.LOW, GPIO.LOW],    # 1
                            [GPIO.LOW, GPIO.LOW, GPIO.HIGH],     # 2
                            [GPIO.LOW, GPIO.HIGH, GPIO.LOW],     # 3
                            [GPIO.LOW, GPIO.HIGH, GPIO.HIGH],    # 4
                            [GPIO.HIGH, GPIO.LOW, GPIO.LOW],     # 5
                            [GPIO.HIGH, GPIO.LOW, GPIO.HIGH],    # 6
                            [GPIO.HIGH, GPIO.HIGH, GPIO.LOW],    # 7
                            [GPIO.HIGH, GPIO.HIGH, GPIO.HIGH]]   # 8

        self.spots_state = {
            0: 0,
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
            7: 0
        }

    def change_entrance_gate_state(self, state):
        time.sleep(0.3)
        if state:       
            GPIO.output(self.entrance_gate, GPIO.HIGH)
        else:
            GPIO.output(self.entrance_gate, GPIO.LOW)

    def change_exit_gate_state(self, state):
        time.sleep(0.3)
        if state:       
            GPIO.output(self.exit_gate, GPIO.HIGH)
        else:
            GPIO.output(self.exit_gate, GPIO.LOW)

    def change_led_full_state(self, state):
        time.sleep(0.3)
        if state:
            GPIO.output(self.led_full, GPIO.HIGH)
        else:
            GPIO.output(self.led_full, GPIO.LOW)    

    def open_entrance_gate(self, channel):
        print("Abrindo cancela de entrada ...")
        self.change_entrance_gate_state(True)
        data = {"msg": "CAR_ENTRANCE", "sender_floor_id": 0}
        self.client.send_message(data)

    def close_entrance_gate(self, channel):
        print("Fechando cancela de entrada ...\n")
        self.change_entrance_gate_state(False)

    def open_exit_gate(self, channel):
        time.sleep(1)
        data = {"msg": "CAR_EXIT", "sender_floor_id": 0}
        self.client.send_message(data)
        print("Abrindo cancela de saída ...")
        self.change_exit_gate_state(True)

    def close_exit_gate(self, channel):
        print("Fechando cancela de saída ...\n")
        self.change_exit_gate_state(False)

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
                    data = {"msg": "CAR_PARKING", "parking_spot_id": i, "sender_floor_id": 0}
                    self.client.send_message(data)

                # Caso algum carro libere alguma vaga
                elif not GPIO.input(self.spot_sensor) and self.spots_state[i]:
                    self.spots_state[i] = 0
                    print(f"Vaga {i} foi desocupada.\n")
                    data = {"msg": "CAR_LEAVING_SPOT", "parking_spot_id": i,  "sender_floor_id": 0}
                    self.client.send_message(data)

                time.sleep(0.05)

            time.sleep(0.5)

    def run(self):
        # Callbacks para lidar com as cancelas de entrada e saída
        GPIO.add_event_detect(self.entrance_opening_sensor, GPIO.RISING, callback=self.open_entrance_gate, bouncetime=200)
        GPIO.add_event_detect(self.entrance_closing_sensor, GPIO.RISING, callback=self.close_entrance_gate, bouncetime=200)
        GPIO.add_event_detect(self.exit_opening_sensor, GPIO.RISING, callback=self.open_exit_gate, bouncetime=200)
        GPIO.add_event_detect(self.exit_closing_sensor, GPIO.RISING, callback=self.close_exit_gate, bouncetime=200)

        # Thread para checar periodicamente as vagas
        spot_thread = threading.Thread(target=self.check_parking_spots_state)
        spot_thread.daemon = True
        spot_thread.start()

        spot_thread.join()
