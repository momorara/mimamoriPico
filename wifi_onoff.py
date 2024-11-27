# -*- coding: utf-8 -*-
#!/usr/bin/python3
"""
2023/5/4
wifiのon-offを行う
osはいないので、やってくれないよ!!
2023/5/7    lib化
2023/05/20  設定ファィルをconfig.pyとした
2023/06/11  ip_addressを返す
v1.0
v1.1  接続状態をwifi_stat として返す 3 なら接続確立成功
"""
import urequests as requests
import network
import utime
import config
import machine

def wifi_onoff(mode):
    if mode == 'on':
        # wifiの電源を入れる
        machine.Pin(23, machine.Pin.OUT).high()
        #自宅Wi-FiのSSIDとパスワードを入力
        ssid,password = config.ID_PASS()

        wlan = network.WLAN(network.STA_IF)
        wlan.active(False)
        utime.sleep(0.1)
        wlan.active(True)
        wlan.connect(ssid, password)

        # Wait for connect or fail
        max_wait =  20
        while max_wait > 0:
            #  wlan.status() が1 から2 そして3 になると接続が確立する。
            print('waiting for connection...',wlan.status())
            if  wlan.status() >= 3:
                if wlan.status() != 3:
                    wlan.active(False)
                break
            if  wlan.status() < 0:
                utime.sleep(5)
                wlan.active(False)
                utime.sleep(0.1)
                wlan.active(True)
                wlan.connect(ssid, password)
            max_wait -= 1
            utime.sleep(1)
        status = wlan.ifconfig()
        # print( 'ip = ' + status[0] )
        return status[0],wlan.status()
        #return status[0],status[1],status[2]
    else:
        wlan = network.WLAN(network.STA_IF)
        if wlan.isconnected():
            wlan.disconnect()
            print('Wi-Fiから切断されました')
        else:
            print('Wi-Fiはoffです')
        return 0,0
    

def main():
    ip_add,wifi_stat = wifi_onoff('on')
    print("ip:",ip_add, " /  stat:",wifi_stat)

if __name__=='__main__':
    main()

