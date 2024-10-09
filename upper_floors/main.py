from connections.server import Server
from model.floor import Floor
import sys

def main(floor_num):
    server = Server(Floor(floor_num))
    server.start()

if __name__ == "__main__":
    floor_num = int(sys.argv[1])
    main(floor_num)