import socket
import threading
import time
from pathlib import Path
from os.path import exists, isdir
from os import mkdir

BS = 32768000

class Client:
    def __init__(self):
        self.s = socket.create_connection(("127.0.0.1",8888,))
        self.p = Path("c://Users//luoruofeng//Desktop", str(self.s.fileno()))
        if not exists(self.p):
            mkdir(self.p)
        threading.Thread(target=self.recv, args=()).start()


    def recv(self):
        pass
        while True:
            while True:
                try:
                    pc = self.s.recv(BS)
                    with open(Path(self.p, "a.mp4"), "ab+") as f:
                        f.write(pc)
                        if pc is not None:
                            print(str(len(pc)))
                    if pc == b"" or pc is None or len(pc) < BS:
                        if pc is not None:
                            print("*")
                        break
                except (ConnectionError,ConnectionResetError) as e:
                    print("remote server close connection!")
                    return
            print("done!")

    def start(self):
        while True:
            content = input("input:")
            p = Path(content)
            if exists(p) and not isdir(p):
                with open(p, "rb+") as f:
                    c = f.read()
                    print(len(c))
                    self.s.send(c)


if __name__=="__main__":
    Client().start()