import socket
import threading
import time
from array import array
from threading import Lock
from loguru import logger
from json import loads

done = "DONE"
BS = 1024

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
        logger.info("start send_part")
        for addr, cs in self.addr_cs.items():
            try:
                logger.info(str(addr))
                cs.sendall(pc)
                logger.info("SEND MESSAGE LENGTH " + str(len(pc)) + " TO " + str(addr))
            except Exception as e:
                logger.info(f"CONNECTION OF RECEVER IS CLOSED! ADDR:{addr}")
                logger.error(e)
                self.lose_conn(cs, addr)
                continue

    def lose_conn(self, cs, addr):
        logger.info(f"LOSE CONNECTION! ADDR:{addr}")
        if addr in self.addr_cs:
            del self.addr_cs[addr]
        cs.close()

    def mes_handle(self,c: socket.socket, a: tuple):
        logger.info(str(a)+" HAVE CONNECTED!")
        while True:
            try:
                pc = c.recv(BS, socket.MSG_WAITALL)
                logger.info("SEND MESSAGE LENGTH "+str(len(pc))+ " FROM " + str(a))
            except (ConnectionError, ConnectionResetError) as e:
                logger.error(e)
                self.lose_conn(c, a)
                return
            self.send_part(pc)
        self.lose_conn(c, a)


if __name__=="__main__":
    logger.add("/logs/server.log", encoding='utf-8', level='INFO')
    logger.add("/logs/server_error.log", encoding='utf-8', level='ERROR')
    Server().start()