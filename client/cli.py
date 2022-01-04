import socket
import threading
import time
from array import array
from pathlib import Path
from os.path import exists, isdir, getsize
from os import mkdir
from threading import Lock
from json import loads,dumps

BS = 32768000
lock = Lock()
name = "NAME"
size = "SIZE"
done = "DONE"
last = "1"
not_last = "0"

class Client:
    def __init__(self):
        self.s = socket.create_connection(("127.0.0.1",8888,))
        self.p = Path("c://Users//luoruofeng//Desktop", str(self.s.fileno()))
        if not exists(self.p):
            mkdir(self.p)
        threading.Thread(target=self.recv, args=()).start()

    def get_file_info(self) -> tuple:
        info_byte = self.s.recv(1024)
        info_str = info_byte.decode("utf-8")
        print(info_str)
        if "name" in info_str and "size" in info_str:
            info = loads(info_str)
            n = info["name"]
            s = info["size"]
            return (n, s,)
        else:
            raise RuntimeError("info wrong!")


    def recv(self):
        while True:
            n, s = self.get_file_info()
            while True:
                try:
                    pc = self.s.recv(BS)
                    if len(pc) <= 0:
                        print("remote server close connection!")
                        return
                    target_file = Path(self.p, n)
                    with open(target_file, "ab+") as f:
                        f.write(pc)
                        f.flush()
                        if pc is not None:
                            print(str(len(pc)))
                        if getsize(target_file) >= s:
                            self.s.send(last.encode())
                            print(f"FILE SIZE IS {getsize(target_file)}. FILE NAME:{n}. GET ALL FILE.")
                            break
                        else:
                            self.s.send(not_last.encode())
                except (ConnectionError,ConnectionResetError) as e:
                    print("remote server close connection!")
                    return
            print("done!")

    def start(self):
        while True:
            content = input("input:\n")
            lock.acquire()
            p = Path(content)
            if exists(p) and not isdir(p):
                info = {"name": p.name,"size": getsize(p)}
                self.s.send(dumps(info).encode("utf-8"))
                first_resp = self.s.recv(1024).decode("utf-8")
                if first_resp != done:
                    raise RuntimeError("file info send failed!")
                with open(p, "rb+") as f:
                    c = f.read()
                    print(f"send data:{len(c)}")
                    self.s.send(c)
            lock.release()

if __name__=="__main__":
    Client().start()