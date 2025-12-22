import time
import threading

class Thing:
    def wait_5(self):
        time.sleep(5)
        print ('waited 5')

    def wait_1(self):
        time.sleep(1)
        print ('waited 1')

    def wait_3(self):
        time.sleep(3)
        print ('waited 3')

    def wait_10(self):
        time.sleep(10)
        print ('waited 10')

thingy1 = Thing()
thingy2 = Thing()

t1 = threading.Thread(target=thingy1.wait_10)
t3 = threading.Thread(target=thingy1.wait_1)
t4 = threading.Thread(target=thingy1.wait_3)
t2 = threading.Thread(target=thingy2.wait_5)


t1.start()
t2.start()
t4.start()
t3.start()
t1.join()
t2.join()
t4.join()
t3.join()