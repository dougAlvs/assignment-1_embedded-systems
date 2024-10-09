from connections.server import Server
from model.floor import Floor

def main():
    server = Server(Floor())
    server.start()

if __name__ == "__main__":
    main()