"""
 2023/08/20
   iR センサーの状態でLED1,LED2 を点灯、消灯させる。
"""
import machine
import time

SW   = machine.Pin(14, machine.Pin.IN)
led1 = machine.Pin(16, machine.Pin.OUT)
led2 = machine.Pin(17, machine.Pin.OUT)

def human_read():
    return SW.value()

def main():

    while True:
        sense = human_read()
        if sense == 1:
            led1.on()
            led2.off()
        if sense == 0:
            led2.on()
            led1.off()           

        print(sense)
        time.sleep(0.1)

if __name__=='__main__':
    main()
