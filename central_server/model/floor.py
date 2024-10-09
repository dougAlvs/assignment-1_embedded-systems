class Floor():
    def __init__(self, floor_num):
        self.floor_num = floor_num
        self.floor_name = ['Térreo', 'Primeiro Andar', 'Segundo Andar'][self.floor_num]

        self.spots_state = [0 for _ in range(8)]
    
        self.cars = []
        self.cars_num = 0

    def park_car(self, parking_spot_id):
        car = self.cars[-1]
        car.parking_spot_id = parking_spot_id
        car.parking_spot_type =  "regular" if parking_spot_id > 2 else "para idosos" if parking_spot_id > 0 else "para portadores de necessidades especiais"

        self.spots_state[parking_spot_id] = 1

        print(f"Vaga ocupada no {self.floor_name}:")
        print(car)


    def leave_car_spot(self, parking_spot_id):
        for car in self.cars:
            if car.parking_spot_id == parking_spot_id:
                car.calculate_parking_value()
                print(f"Vaga desocupada no {self.floor_name}")
                print(car)
                self.spots_state[parking_spot_id] = 0
                self.cars.remove(car) 
                break

    def check_occupied_spots(self):
        return sum(self.spots_state[:1]), sum(self.spots_state[1:3]), sum(self.spots_state[3:])

