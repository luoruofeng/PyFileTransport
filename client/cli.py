import socket
import threading
import time
from array import array
from pathlib import Path
from os.path import exists, isdir
from os import mkdir

BS = 32768000

class Client:
    def __init__(self):
        self.s = socket.create_connection(("hbox.top",8888,))
        self.p = Path("c://Users//luoruofeng//Desktop", str(self.s.fileno()))
        if not exists(self.p):
            mkdir(self.p)
        threading.Thread(target=self.recv, args=()).start()


    def recv(self):
        pass
        while True:
            while True:
                try:
                    pc, ancdata, flags, addr = self.s.recvmsg(BS)
                    fds = array.array("u")  # Array of ints
                    for cmsg_level, cmsg_type, cmsg_data in ancdata:
                        if cmsg_level == socket.SOL_SOCKET and cmsg_type == socket.SCM_RIGHTS:
                            # Append data, ignoring any truncated integers at the end.
                            fds.frombytes(cmsg_data[:len(cmsg_data) - (len(cmsg_data) % fds.itemsize)])
                    print(fds)

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
                    fds = ["name1"]
                    self.s.sendmsg(c, [(socket.SOL_SOCKET, socket.SCM_RIGHTS, array.array("i", fds))])


if __name__=="__main__":
    Client().start()