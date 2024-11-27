# -*- coding: utf-8 -*-
#!/usr/bin/python3
"""
2023/08/20  picoMimamori開発開始
2023/08/23  人感センサー、スイッチ、ambientをmainから切り離す
2023/08/24  LED操作
2023/08/25  人感センサーをワンショットでやるとエラー（誤信号1回）でambient表示してしまう。
            複数回カウントできるようにする。
            とりあえず、累積値をそのままambientに投げる
            ・メール送信
2023/08/28  SW押下されMAIL送信時のLED表示変更
2023/11/25  新基板への対応
2023/11/26  湿度表示
2023/11/27  非表示設定
2024/08/23  mqtt対応
2024/11/25  夜間LEDとOLEDを消灯対策 夜間の時間設定はconfig.pyで行う。
            初回amboentで403となる対策

mimamori_06
"""
main_py = 0 # 1の時は自己リブートを有効にする。

import time
import gc
import sys
import machine

import lib_LED
import wifi_onoff
import config

import lib_SW
import lib_iR
import lib_Cds
import lib_AHT10
import lib_wbgt

import SSD1306_m
import lib_NTP

import mailSend_01
import ambient

import mqtt_file
import mqtt_pub
import utime
"""
print(config.nigth_mode())

if config.nigth_mode() == 0: # ナイトモードでなければ、以下実行
"""

# Ambient対応 
ch_ID,write_KEY  = config.ambi()
"""                チャネルID   ライトキー        """
am = ambient.Ambient(ch_ID, write_KEY)
""""""""""""""""""""""""""""""""""""""""""""""""""
measu_cycle = config.measu_cycle()
wifi = config.wifi_set ()
print( "wifi使用設定 :",wifi)

hosei_temp,hosei_humdi = config.hosei()
print( "温度補正値:",hosei_temp)
print( "湿度補正値:",hosei_humdi)
# 補正自体はlib_AHT10.pyで実施

mail_onoff,MailServerName,UserName,UserPass,toMailAddres,mail_title,mail_body = config.mail_setting()
#print(mail_onoff,MailServerName,UserName,UserPass,toMailAddres,mail_title,mail_body)

led1 = machine.Pin(16, machine.Pin.OUT)
led1.off()
led2 = machine.Pin(17, machine.Pin.OUT)
led2.off()

# 非表示設定
WBGT_hidden,human_hidden = config.hidden_setting()

# データがNoneの場合は欠損処理をする
def ambient(temp,Cds,human,SW,wbgt,humi,stat=1):
    # 非表示設定
    if WBGT_hidden  >  wbgt :wbgt  = 0
    if human_hidden >= human:human = human/10
    res = am.send({"d1": temp,"d2":Cds,"d3":human,"d4":SW,"d5": stat,"d6":wbgt,"d7":humi})
    # print(res.status_code)
    if res.status_code == 200:# ambient成功
        print("ok")
        # mqttのtopicを決定
        topic = mqtt_file.topic_get()
        print(topic)
        # topicに温度を送信
        mqtt_pub.mqtt_send(topic,temp)
    else:
        print("NG-1",res.status_code)
        time.sleep(1)
        res = am.send({"d1": temp,"d2":Cds,"d3":human,"d4":SW,"d5": stat,"d6":wbgt,"d7":humi})
        print(res.status_code)
        if res.status_code == 200:# ambient成功
            print("ok")
            # mqttのtopicを決定
            topic = mqtt_file.topic_get()
            print(topic)
            # topicに温度を送信
            mqtt_pub.mqtt_send(topic,temp)
        else:
            print("NG-2",res.status_code)

def ambient_stat(stat):
    try:
        res = am.send({"d5": stat})
    except:
        pass

def keisoku(human,SW):
    #print("keisoku")
    temp,humi = lib_AHT10.aht10(1)
    Cds  = lib_Cds.Cds(1)

    # human信号を累積する 人感センサー誤動作対策
    once_human = lib_iR.human_read()
    if once_human == 1 and human == 0:
        # human初期は0 次は3,4,5,6となる
        human = 2
    human = human + once_human
    # LED2を1秒点灯
    if once_human == 1:
        # print("nigth_mode:",config.nigth_mode())
        if config.nigth_mode() == 0: # ナイトモードでなければ、以下実行
            led2.on()
            time.sleep(1)
        led2.off()
    # 一度onになったらambient_sendまでは1のまま
    # if human == 0:
    #     human = lib_iR.human_read()
    #     if human == 1:human = 3

    if SW == 0:
        SW = lib_SW.SW_read()
        if SW == 1:SW = 2
        
    #print("keisoku:",temp,Cds,human,SW)
    if human != 0:
        if config.nigth_mode() == 0: # ナイトモードでなければ、以下実行
            led1.on()
    else:
        led1.off()
    if SW != 0:
        if config.nigth_mode() == 0: # ナイトモードでなければ、以下実行
            led2.on()
    else:
        led2.off()

    # 夏季 暑さ指数
    try:
        wbgt = lib_wbgt.calc(temp,humi)
    except:
        wbgt = 0

    return temp,humi,Cds,human,SW,wbgt

# bootSWの状態を見る
import machine
led = machine.Pin('LED', machine.Pin.OUT)
BOOTSEL_PIN = 22
bootsel_button = machine.Pin(BOOTSEL_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
def bootSW():
    if rp2.bootsel_button() == 1:
        return 1
    else:
        return 0

# 各データをambientに投げる
def ambient_send(temp,Cds,human,SW,wbgt,humi):
    # pico-LEDを点滅
    for i in range(3):
        # print("nigth_mode:",config.nigth_mode())
        if config.nigth_mode() == 0: # ナイトモードでなければ、以下実行
            lib_LED.LEDonoff()

    UTC_OFFSET = 9 * 60 * 60       
    now = time.localtime(time.time() + UTC_OFFSET)
    print(now,"ambient send")
    
    # ambientにデータを投げる
    try:
        ambient(temp,Cds,human,SW,wbgt,humi)
        time.sleep(10)
    except:  
        print("amb_err:1")
        time.sleep(10)
        ambient_stat(2)
        time.sleep(10)
        try:
            ambient(temp,Cds,human,SW,wbgt,humi)
            time.sleep(10)
        except:
            print("amb_err:2")
            time.sleep(60)
            ambient_stat(3)
            time.sleep(10)
            try:
                ambient(temp,Cds,human,SW,wbgt,humi)
                time.sleep(10)
            except:
                print("amb_err:3")
                time.sleep(10)
                ambient_stat(4) 
                time.sleep(10)
                if main_py == 1:
                    # リブート
                    machine.reset()
                print("amb_err:e")


def main():
    # プログラム起動準備
    print("start")
    SSD1306_m.OLED_mes("program start")
    lib_LED.LEDonoff()
    temp,humi,Cds,human,SW,wbgt = 0,0,0,0,0,0
    temp,humi,Cds,human,SW,wbgt = keisoku(human,SW)
    print(" 初期",temp,humi,Cds,human,SW,wbgt)
    SSD1306_m.OLED(temp,Cds,human,SW)
    # wifi 接続
    ip_add = "no connect"
    wifi_stat = 0
    if wifi == 1:
        print("wifi-start")
        ip_add,wifi_stat = wifi_onoff.wifi_onoff('on')
        # NTP にて時刻合わせ
        lib_NTP.NTP_set()
        lib_LED.LEDonoff()
        lib_LED.end_LED()
    print("ip:",ip_add,wifi_stat)
    SSD1306_m.OLED_mes(ip_add)
    time.sleep(3)
    ambient_stat(10)        # テスト 10
    time.sleep(3)

    # ループ
    print()
    print("loop start")
    SSD1306_m.OLED_mes("loop start")
    UTC_OFFSET = 9 * 60 * 60  
    once_time = 99
    oled_off_count = 3 #ambient送信後 3回のループで消灯
    once_mail = 0
    while True:
        now = time.localtime(time.time())
        # 各種機能の起動

        # センサー測定
        # temp,Cdsはリアル測定数値
        # human,SWは一度onになったらambient_send後にリセット
        temp,humi,Cds,human,SW,wbgt = keisoku(human,SW)

        #print('温度:',temp,' 明暗:',Cds,' 人感:',human,' SW:',SW)
        # 人感かswが1になったら表示しambient送信後に消灯
        if human != 0 or SW != 0:
            if config.nigth_mode() == 0: # ナイトモードでなければ、以下実行
                SSD1306_m.OLED(temp,Cds,human,SW)
        else:
            if oled_off_count < 0 :
                SSD1306_m.OLED_mes(" ")
                oled_off_count = 3
            else:
                oled_off_count = oled_off_count - 1

        # measu_cycle毎に1回だけ実行
        if now[4] % measu_cycle == 0 and now[4] != once_time :
            ambient_send(temp,Cds,human,SW,wbgt,humi)
            human,SW = 0,0
            once_time = now[4]
            once_mail = 0


        # SWが押されたらメール処理
        # メールがonになっていることを確認して、1回メールを送信する
        # 続けて送信しないためにonce_mailで制御
        if SW == 2 and mail_onoff == 1 and once_mail == 0:
            print("mail送信")
            for i in range(6):
                led2.off()
                time.sleep(0.2)
                led2.on()
                time.sleep(0.3)
            once_mail = 1
            #メール送信処理
            mailSend_01.mailSend(mail_title,mail_body,toMailAddres)


        # bootスイッチが押されたらプログラム終了
        if bootSW() == 1:
            #print(bootSW())
            lib_LED.end_LED()
            sys.exit()

        now = time.localtime(time.time() + UTC_OFFSET)
        print("Time",now[3],":",now[4],".",now[5],"  ",'温度:',temp,'湿度:',humi,' 明暗:',Cds,' 人感:',human,' SW:',SW,"wbgt:",wbgt,"night:",config.nigth_mode())
        # 午前1:10にリブート +9:00しているので、補正すること
        if now[3] == 5 and now[4] == 50: #5:50
            try:
                time.sleep(6) 
                ambient_stat(11)        # テスト 11
                time.sleep(10)
                if main_py == 1:
                    SSD1306_m.OLED_mes("reboot time")
                    time.sleep(60)      #最悪でも繰り返さない
                    # リブート
                    machine.reset()
                lib_NTP.NTP_set()
                SSD1306_m.OLED_mes("NTP")
                time.sleep(60)          # テスト
                ambient_stat(5)         # テスト 5
                time.sleep(10)
                print("NTP")
            except:
                time.sleep(10)
                ambient_stat(14)         # テスト 14
                time.sleep(10)
        gc.collect()  #ガーベージコレクション

        # 2秒程度にループ
        time.sleep(1)
        # LED点滅
        if config.nigth_mode() == 0: # ナイトモードでなければ、以下実行
            lib_LED.LEDonoff()
         
if __name__=='__main__':
    # main()
    try:
        main()
    except:
        time.sleep(10)
        ambient_stat(12)
        time.sleep(10)
        SSD1306_m.OLED_mes("main err")
        time.sleep(2)
        print("main-try /main_py:",main_py)
        # 想定されていないエラーが発生してmainがこけた場合
        # ここに来て、リブートするが、エラーが継続している場合ループしてしまう。
        # そんな時は、リブートする前にbootスイッチを押すことで、プログラムを終了させる。
        for i in range(10):
            if bootSW() == 1:
                #print(bootSW())
                lib_LED.end_LED()
                sys.exit()
                main_py = 0
            lib_LED.LEDonoff()
            print("main-try /i:", i)
            mes = "main-try /i:" + str(i)
            SSD1306_m.OLED_mes(mes)

        if main_py == 1:
            time.sleep(10)
            ambient_stat(13) 
            time.sleep(10)
            SSD1306_m.OLED_mes("reboot")
            print("main-try / リブート")
            # リブート
            machine.reset()

"""
ambient_statによるエラー情報等の表示
1 通常
2 ambient送信異常 1回目
3 ambient送信異常 2回目
4 ambient送信異常 3回目
5 定時リブート未実行時NTP
6 温度異常
7 湿度異常
8 データ異常時のambient送信
9 データ異常時のambient送信異常
10 main start
11 定時リブート
12 mainエラー
13 mainエラー時のリブート
14 定時リブート失敗
"""