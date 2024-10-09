from uuid import uuid4
from time import time
from datetime import datetime

class Car():
    def __init__(self):
        self.id = str(uuid4())[:3]
        self.entrance_time = time()
        self.parking_spot_id = None
        self.parking_spot_type = None
        self.exit_time = None
        self.parking_fee = 0.1
        self.parking_value = 0.0

    def calculate_parking_value(self):
        self.exit_time = time()
        delta = (self.exit_time - self.entrance_time) // 60 
        self.parking_value = self.parking_fee * delta

    def format_time(self, timestamp):
        return datetime.fromtimestamp(timestamp).strftime('%H:%M')

    def __repr__(self):
        entrance_time_formatted = self.format_time(self.entrance_time)
        if self.exit_time:
            delta = (self.exit_time - self.entrance_time) // 60 
            exit_time_formatted = self.format_time(self.exit_time)
            return (f"Carro de ID: {self.id} - Vaga {self.parking_spot_type} de ID: {self.parking_spot_id}\n" +
                    f"Horário Entrada: {entrance_time_formatted} - Horário Saida: {exit_time_formatted}\n" +
                    f"Minutos de estadia: {delta} - Valor: R$ {self.parking_value:.2f}\n")
        else: 
            return (f"Carro de ID: {self.id} - Vaga {self.parking_spot_type} de ID: {self.parking_spot_id}\n" +
                    f"Horário Entrada: {entrance_time_formatted}\n")