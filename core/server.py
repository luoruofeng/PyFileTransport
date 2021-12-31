import socket
import threading
import time
from threading import Lock

BS = 32768000

class Server:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.allc = []

    def start(self):
        self.s.bind(("0.0.0.0", 8888,))
        self.s.listen(100)
        t = threading.Thread(target=self.recv, args=())
        t.start()
        t.join()
        print("server stop!!!!")

    def end(self):
        for i in self.allc:
            self.allc.remove(i)
            i.close()
        self.s.close()


    def recv(self):
        while True:
            c, a = self.s.accept()
            self.allc.append(c)
            threading.Thread(target=self.mes_handle,args=(c, a,)).start()
        self.end()

    def send_part(self, pc):
        time.sleep(3)
        for i in self.allc:
            i.sendall(pc)

    def mes_handle(self,c: socket.socket, a: str):
        print(str(a)+" connected!")
        while True:
            while True:
                try:
                    pc = c.recv(BS)
                    print("-----"+str(len(pc)))
                    if pc == b"" or pc is None:
                        break
                    threading.Thread(target=self.send_part, args=(pc,)).start()
                    if len(pc) < BS:
                        break
                except Exception as err:
                    self.allc.remove(c)
                    c.close()
                    return
            print("get!!")
        self.allc.remove(c)
        c.close()


if __name__=="__main__":
    Server().start()