# A dotter while I'm thinking

import itertools
import sys
import threading
import time

def StrReplace(ts:str,ds:str,index:int|list,is_special=False): # <sp>
    if (type(index) == list):
        for i in index:
            ts = StrReplace(ts,"麤", i,True)
        return ts.replace("麤", ds,-1)
    elif (type(index) == int):
        if (is_special):
            return ts[:index] + "麤" + ts[index+1:]
        else:
            return ts[:index] + ds + ts[index+1:]

class Symbols:
    @staticmethod
    def buildlr(s = "==",length=10,head="[",end="]", cross = True):
        alls = s * length
        star = []
        revs = []

        if (not cross):
            for i in range(0,length):
                star.append(head + " "*i + s + " "*(length-i) + end)
                revs.append(head + " "*(length-i) + s + " "*i + end)
            return star + revs
        else:
            total_len  = length+ 2 *len(s)
            # totalmides = " "*total_len
            for i in range(0,length+len(s)):
                this_s = " "*i + s + " "*(length-i)
                star.append(head + this_s[len(s)-1:length+len(s)] + end)
            return star

    dot    = ['.','..','..']
    slash  = ["\\","|","/"]
    abc    = ["a","a b","a b c"]
    lvnm   = ["l","V","N","M"]
    oneTO  = [1,2,3,4,5,6,7,8,9]
    facelr = buildlr("(*´∀`)~♥",cross=False)
    starlr = buildlr("*")

class dotter:

    # A dotter while I'm thinking

    def __init__(self, message: str = "Thinking", delay: float = 0.5,cycle:list[int]=Symbols.slash) -> None:
        self.spinner = itertools.cycle(cycle)
        self.delay = delay
        self.message = message
        self.running = False
        self.dotter_thread = None

    def dot(self):
        while self.running:
            sys.stdout.write(f"{self.message} {next(self.spinner)} \r")
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write(f"\r{' ' * (len(self.message) + 6)}\r")

    def update_message(self, new_message, delay=0.1):
        time.sleep(delay)
        sys.stdout.write(
            f"\r{' ' * (len(self.message) + 6)}\r"
        )  # Clear the current message
        sys.stdout.flush()
        self.message = new_message

    def __enter__(self):
        self.running = True
        self.dotter_thread = threading.Thread(target=self.dot)
        self.dotter_thread.start()



    def __exit__(self,*args) -> None:
        self.running = False
        if self.dotter_thread is not None:
            self.dotter_thread.join()
        sys.stdout.write(f"\r{' ' * (len(self.message) + 2)}\r")
        sys.stdout.flush()


if __name__ == "__main__":
    from time import sleep

    with dotter("Thinking", 0.2,cycle = Symbols.facelr):
        sleep(10)