"""
 2023/08/22 sw1,0を逆にする
 2023/9/23   タクトスイッチをソフトプルアップとした
"""
import machine
import time

SW   = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)
led1 = machine.Pin(16, machine.Pin.OUT)
led2 = machine.Pin(17, machine.Pin.OUT)

def SW_read():
    if SW.value() == 1:
        return 0
    if SW.value() == 0:    
        return 1

def main():

    while True:
        sense = SW_read()
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
