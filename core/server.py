import socket
import threading
import time
from array import array
from threading import Lock
from loguru import logger
from json import loads
import re


done = "DONE"
BS = 1024
HEAD_LEN = 256

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
        logger.info("start send_part. munber:"+str(self.addr_cs))
        for addr, cs in self.addr_cs.items():
            try:
                logger.info(str(addr))
                cs.sendall(pc)
                logger.info("SEND MESSAGE LENGTH " + str(len(pc)) + " TO " + str(addr))
            except Exception as e:
                logger.info(f"CONNECTION OF RECEVER IS CLOSED! ADDR:{addr}")
                logger.error(e)
                self.lose_conn(cs, addr)
                logger.info("123")
                continue

    def lose_conn(self, cs, addr):
        logger.info(f"LOSE CONNECTION! ADDR:{addr}")
        if addr in self.addr_cs:
            del self.addr_cs[addr]
        logger.info(f"1closed client! "+str(addr))
        cs.close()
        logger.info(f"2closed client! "+str(addr))


    def rate_of_progress(self,current_size,totol_size) -> float:
        current_size += BS
        return (current_size/totol_size *100 , current_size,)


    def check_first_chunk(self, content: bytes) -> tuple:
        r = re.compile(b"^{.*name.*size.*}").match(content)
        if r == None:
            return None
        head = r.group(0)
        if not head:
            return None
        info = loads(head.decode("utf-8"))
        name = info["name"]
        size = info["size"]
        return (name, size)


    def mes_handle(self,c: socket.socket, a: tuple):
        logger.info(str(a)+" HAVE CONNECTED!")
        name, size, current_size= None, None, None
        while True:
            try:
                pc = c.recv(BS, socket.MSG_WAITALL)
                head = self.check_first_chunk(pc)
                if head:
                    name, size, current_size = head[0], head[1], 0
                rate, current_size = self.rate_of_progress(current_size, size)
                logger.info("RECEIVE FILE:"+name+". DATA RATE OF PROGRESS:"+str(rate)+"%")
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