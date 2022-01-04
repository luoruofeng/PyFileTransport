import socket
import threading
import time
from array import array
from threading import Lock
from loguru import logger
from json import loads

done = "DONE"
BS = 32768000

class Server:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr_cs = {}

    def start(self):
        self.s.bind(("0.0.0.0", 8888,))
        self.s.listen(100)
        t = threading.Thread(target=self.recv, args=())
        t.start()
        t.join()
        logger.info("server stop!!!")

    def end(self):
        for i in self.allc:
            self.allc.remove(i)
            i.close()
        self.s.close()


    def recv(self):
        while True:
            c, a = self.s.accept()
            self.addr_cs[a] = c
            threading.Thread(target=self.mes_handle,args=(c, a,)).start()
        self.end()

    def send_part(self, pc):
        try:
            for addr, cs in self.addr_cs.items():
                cs.sendall(pc)
        except Exception as e:
            logger.info(f"recver's connection closed! addr:{addr}")
            raise e
    def get_file_info(self, c: socket.socket, a: str) -> tuple:
        info_byte = c.recv(1024)
        info_str = info_byte.decode("utf-8")
        if "name" in info_str and "size" in info_str:
            for addr, cs in self.addr_cs.items():
                if cs != c:
                    cs.send(info_byte)
            c.send(done)
            info = loads(info_str)
            name = info["name"]
            size = info["size"]
            return (name, size,)
        else:
            raise RuntimeError("info wrong!")

    def mes_handle(self,c: socket.socket, a: tuple):
        logger.info(str(a)+" connected!")
        while True:
            name, size = self.get_file_info(c, a)
            while True:
                try:
                    pc = c.recv(BS)
                except Exception as err:
                    #TODO 发送人 断开 需要告诉其他人 不用接收了 可以删除刚才的或者什么都不做
                    del self.addr_cs[a]
                    c.close()
                    return
                try:
                    t = threading.Thread(target=self.send_part, args=(pc,))
                    t.start()
                    t.join()
                    #TODO 这样写代码还是有纰漏 因为send_part没有全部发送就会执行join
                except:
                    continue
                break
            logger.info("GET!!")
        self.allc.remove(c)
        c.close()


if __name__=="__main__":
    logger.add("/logs/server.log", encoding='utf-8', level='INFO')
    logger.add("/logs/server_error.log", encoding='utf-8', level='ERROR')
    Server().start()