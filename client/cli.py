import socket
import threading
import re
from array import array
from pathlib import Path
from os.path import exists, isdir, getsize
from os import mkdir
from json import loads,dumps
from struct import *

BS = 1 << 10
HEAD_LEN = 1 << 8
TARGET_DIR = "c://Users//luoruofeng//Desktop"

class Client:
    def __init__(self):
        self.s = socket.create_connection(("hbox.top",8888,))
        self.tp = Path(TARGET_DIR, str(self.s.fileno()))
        if not exists(self.tp):
            mkdir(self.tp)
        threading.Thread(target=self.recv, args=()).start()
        print("CLOSE CONNECTION!!!!")
        self.s.close()


    def check_first_chunk(self, content: bytes) -> tuple:
        r = re.compile(b"^{.*name.*size.*}").match(content)
        if r == None:
            return None
        head = r.group(0)
        if not head:
            return None
        data = content[HEAD_LEN:]
        info = loads(head.decode("utf-8"))
        name = info["name"]
        size = info["size"]
        return (name, size, data)


    def get_pure_data(self,data):
        print("start pure")
        if data.endswith(b"\x00"):
            print("start pure2")
            empty_index = re.search(b"\x00+$", data).span()[0]
            print(data)
            data = data[:empty_index]
            print(data)
            return data



    def recv(self):
        name, size = None, None
        while True:
            try:
                data = self.s.recv(BS, socket.MSG_WAITALL)
                if len(data) <= 0:
                    print("CONNECTION OF REMOTE SERVER FAILED!")
                    return
                head = self.check_first_chunk(data)
                if head is not None:
                    name, size, data = head[0], head[1], head[2]
                if not name:
                    print("TOO LATE TO ACCEPT DATA!")
                    return
                target_file = Path(self.tp, name)
                with open(target_file, "ab+") as f:
                    if getsize(target_file) + HEAD_LEN + BS >= size:
                        # this is latest chunk
                        data = self.get_pure_data(data)
                    f.write(data)
                    f.flush()
                    if data is not None:
                        print(str(len(data)))
                    print("-")
                    if getsize(target_file) >= size:
                        print(f"FILE SIZE IS {getsize(target_file)}. FILE NAME:{name}. GET ALL FILE.")
            except (ConnectionError,ConnectionResetError) as e:
                print("CONNECTION OF REMOTE SERVER FAILED!")
                return
        print("DONE!")


    def get_send_size(self, data):
        content_size = HEAD_LEN + len(data)
        remainder = content_size % BS
        if remainder != 0:
            content_size = content_size + (BS - remainder)
        return content_size

    def get_head(self, path, send_size) -> bytes:
        head_dict = {"name": path.name, "size": send_size}
        return pack(f"{HEAD_LEN}s".encode(), dumps(head_dict).encode("utf-8"))

    def content(self, head, data, send_size):
        return pack(f"{send_size}s".encode(), head + data)

    def start(self):
        while True:
            content = input("input:\n")
            p = Path(content)
            if exists(p) and not isdir(p):
                with open(p, "rb+") as f:
                    data = f.read()
                    send_size = self.get_send_size(data)
                    head = self.get_head(p, send_size)
                    content = self.content(head, data, send_size)
                    print(f"SEND SIZE:{len(content)},HEAD SIZE:{len(head)} FIZE SIZE{len(data)}:")
                    self.s.sendall(content)

if __name__=="__main__":
    Client().start()