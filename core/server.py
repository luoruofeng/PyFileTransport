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

    def send_part(self, pc, handle_result):
        for addr, cs in self.addr_cs.items():
            print(str(addr))
            try:
                cs.sendall(pc)
                has_done = bool(int(cs.recv(1024).decode("utf-8")))
                if bool(has_done):
                    handle_result.append((addr, True))
            except Exception as e:
                logger.info(f"recver's connection closed! addr:{addr}")
                handle_result.append((addr, False))
                if addr in self.addr_cs:
                    del self.addr_cs[addr]
                continue


    def get_file_info(self, c: socket.socket, a: str) -> tuple:
        info_byte = c.recv(1024)
        info_str = info_byte.decode("utf-8")
        if "name" in info_str and "size" in info_str:
            for addr, cs in self.addr_cs.items():
                cs.send(info_byte)
            c.send(done.encode("utf-8"))
            info = loads(info_str)
            name = info["name"]
            size = info["size"]
            return (name, size,)
        else:
            raise RuntimeError("INFO IS WRONG!")

    def mes_handle(self,c: socket.socket, a: tuple):
        logger.info(str(a)+" connected!")
        while True:
            name, size = self.get_file_info(c, a)
            logger.info(f"GET INFO FROM {str(a)}!")
            handle_result = []
            while True:
                try:
                    pc = c.recv(BS)
                except Exception as err:
                    #TODO 发送人 断开 需要告诉其他人 不用接收了 可以删除刚才的或者什么都不做
                    logger.info(str(err))
                    del self.addr_cs[a]
                    c.close()
                    return
                try:
                    self.send_part(pc, handle_result)
                    #TODO 这样写代码还是有纰漏 因为send_part没有全部发送就会执行join
                except:
                    continue
                if len(self.addr_cs) == len(handle_result):
                    break
                    logger.info(f"SEND DONE! result:{handle_result}")
        self.allc.remove(c)
        c.close()


if __name__=="__main__":
    logger.add("/logs/server.log", encoding='utf-8', level='INFO')
    logger.add("/logs/server_error.log", encoding='utf-8', level='ERROR')
    Server().start()