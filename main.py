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

# ambient停止を受けて別サービスに移行
2026/11/17  wdtの追加　各モジュールも変更

wdt追加で
mimamoriPico_wdt_01 と改名
"""
main_py = 0 # 1の時は自己リブートを有効にする。

# -*- coding: utf-8 -*-
# ==================================================
# mimamoriPico_wdt_02.py
# Raspberry Pi Pico W / MicroPython
# 見守りシステム メインプログラム
# WDT・通信エラー対策版
# 2026/11/18
# ==================================================
import time
import gc
import sys
import machine
import rp2
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
import mqtt_file
import mqtt_pub
import utime
import blynk
import MiniViz
import wifi_connect
from machine import WDT
# --------------------------------------------------
# 基本設定
# --------------------------------------------------
main_py = 0
WDT_TIMEOUT = 8000
UTC_OFFSET = 9 * 60 * 60
# --------------------------------------------------
# 設定値取得
# --------------------------------------------------
try:
    measu_cycle = int(config.measu_cycle())
    if measu_cycle <= 0:
        measu_cycle = 1
except Exception as e:
    print("測定周期設定エラー:", repr(e))
    measu_cycle = 1
try:
    wifi = int(config.wifi_set())
except Exception as e:
    print("Wi-Fi設定エラー:", repr(e))
    wifi = 0
print("wifi使用設定:", wifi)
try:
    hosei_temp, hosei_humdi, press = config.hosei()
except Exception as e:
    print("補正値設定エラー:", repr(e))
    hosei_temp, hosei_humdi, press = 0, 0, 900
print("温度補正値:", hosei_temp)
print("湿度補正値:", hosei_humdi)
try:
    WBGT_hidden, human_hidden = config.hidden_setting()
except Exception as e:
    print("非表示設定エラー:", repr(e))
    WBGT_hidden, human_hidden = 0, 0
# --------------------------------------------------
# GPIO初期化
# --------------------------------------------------
try:
    led1 = machine.Pin(16, machine.Pin.OUT, value=0)
    led2 = machine.Pin(17, machine.Pin.OUT, value=0)
except Exception as e:
    print("LED初期化エラー:", repr(e))
    led1 = None
    led2 = None
# --------------------------------------------------
# 共通エラー処理
# --------------------------------------------------
def safe_call(name, func, *args, default=None, wdt=None):
    if wdt is not None:
        try:
            wdt.feed()
        except Exception:
            pass
    try:
        return func(*args)
    except Exception as e:
        print(name + "エラー:", repr(e))
        return default
    finally:
        if wdt is not None:
            try:
                wdt.feed()
            except Exception:
                pass
# --------------------------------------------------
# LED制御
# --------------------------------------------------
def led_off():
    try:
        if led1 is not None:
            led1.off()
        if led2 is not None:
            led2.off()
    except Exception as e:
        print("LED消灯エラー:", repr(e))
# --------------------------------------------------
# 時刻記録
# --------------------------------------------------
def time_stamp(no):
    try:
        t = time.time() + UTC_OFFSET
        tm = time.localtime(t)
        date_str = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d} {}".format(
            tm[0], tm[1], tm[2], tm[3], tm[4], tm[5], no
        )
        print("現在日時TS:", date_str)
        mode = "w" if no == -1 else "a"
        with open("time_stamp.txt", mode) as f:
            f.write(date_str + "\n")
    except Exception as e:
        print("時刻記録エラー:", repr(e))
# --------------------------------------------------
# センサー測定
# --------------------------------------------------
last_temp = 0
last_humi = 0
def keisoku(human, SW):
    global last_temp, last_humi
    time_stamp(2)
    # 温度・湿度
    result = safe_call("AHT10", lib_AHT10.aht10, 1)
    if result is not None:
        try:
            temp, humi = result
            if isinstance(temp, (int, float)) and isinstance(humi, (int, float)):
                last_temp = temp
                last_humi = humi
            else:
                print("AHT10データ異常")
        except Exception as e:
            print("AHT10データ処理エラー:", repr(e))
    temp, humi = last_temp, last_humi
    # CDS
    cds_value = safe_call("CDS", lib_Cds.Cds, 1, default=0)
    # 人感センサー
    once_human = safe_call("IR", lib_iR.human_read, default=-1)
    if once_human == 1 and human == 0:
        human = 2
    if once_human == 1:
        human += 1
        try:
            if config.nigth_mode() == 0 and led2 is not None:
                led2.on()
                time.sleep_ms(1000)
                led2.off()
        except Exception as e:
            print("人感LEDエラー:", repr(e))
    # スイッチ
    if SW == 0:
        sw_value = safe_call("SW", lib_SW.SW_read, default=-1)
        if sw_value == 1:
            SW = 2
        elif sw_value == 0:
            SW = 0
    # LED表示
    try:
        if config.nigth_mode() == 0:
            if led1 is not None:
                led1.on() if human != 0 else led1.off()
            if led2 is not None:
                led2.on() if SW != 0 else led2.off()
    except Exception as e:
        print("LED表示エラー:", repr(e))
    # WBGT
    wbgt = safe_call("WBGT", lib_wbgt.calc, temp, humi, default=0)
    return temp, humi, cds_value, human, SW, wbgt
# --------------------------------------------------
# BOOTSELスイッチ
# --------------------------------------------------
def bootSW():
    try:
        return 1 if rp2.bootsel_button() else 0
    except Exception as e:
        print("BOOTSEL読み取りエラー:", repr(e))
        return 0
# --------------------------------------------------
# 起動処理
# --------------------------------------------------
def startup():
    print("start")
    safe_call("OLED起動表示", SSD1306_m.OLED_mes, "program start")
    safe_call("LED起動", lib_LED.LEDonoff)
    temp, humi, cds_value, human, SW, wbgt = keisoku(0, 0)
    print("初期:", temp, humi, cds_value, human, SW, wbgt)
    safe_call("OLED初期表示", SSD1306_m.OLED, temp, cds_value, human, SW)
    ip_add = "no connect"
    if wifi == 1:
        ip_add = safe_call("Wi-Fi接続", wifi_onoff.wifi_onoff, "on", default="no connect")
        safe_call("NTP時刻設定", lib_NTP.NTP_set)
        safe_call("LED終了表示", lib_LED.LEDonoff)
        safe_call("LED終了", lib_LED.end_LED)
    print("ip:", ip_add)
    safe_call("OLED IP表示", SSD1306_m.OLED_mes, str(ip_add))
    time.sleep(10)
    return temp, humi, cds_value, human, SW, wbgt
# --------------------------------------------------
# メイン処理
# --------------------------------------------------
def main():
    temp, humi, cds_value, human, SW, wbgt = startup()
    wdt = WDT(timeout=WDT_TIMEOUT)
    print("loop start")
    safe_call("OLEDループ表示", SSD1306_m.OLED_mes, "loop start")
    once_time = 99
    oled_off_count = 3
    once_mail = 0
    once_ntp_day = -1
    while True:
        try:
            wdt.feed()
            time_stamp(10)
            now = time.localtime(time.time())
            # センサー測定
            temp, humi, cds_value, human, SW, wbgt = keisoku(human, SW)
            wdt.feed()
            # 人感・SW表示
            if human != 0 or SW != 0:
                if safe_call("夜間設定", config.nigth_mode, default=1) == 0:
                    safe_call("OLED表示", SSD1306_m.OLED, temp, cds_value, human, SW)
            else:
                if oled_off_count < 0:
                    safe_call("OLED消灯", SSD1306_m.OLED_mes, " ")
                    oled_off_count = 3
                else:
                    oled_off_count -= 1
            time_stamp(11)
            # 定時データ送信
            if now[4] % measu_cycle == 0 and now[4] != once_time:
                print("定時データ送信開始")
                # Wi-Fi維持
                safe_call("Wi-Fi維持", wifi_connect.keep_alive, wdt=wdt)
                # Blynk
                safe_call("Blynk送信", blynk.send_data, temp, humi, press, cds_value, human, wdt=wdt)
                # MiniViz
                safe_call("MiniViz送信", MiniViz.send_data, temp, humi, press, cds_value, human, wdt=wdt)
                # 送信後に人感・SWをリセット
                human, SW = 0, 0
                once_time = now[4]
                once_mail = 0
                # MQTT
                topic = safe_call("MQTTトピック取得", mqtt_file.topic_get, default=None)
                if topic is not None:
                    print(topic)
                    safe_call("MQTT送信", mqtt_pub.mqtt_send, topic, temp, wdt=wdt)
            # SWメール処理
            if SW == 2 and once_mail == 0:
                print("SWが押された")
                try:
                    for i in range(6):
                        if led2 is not None:
                            led2.off()
                        time.sleep_ms(200)
                        if led2 is not None:
                            led2.on()
                        time.sleep_ms(300)
                        wdt.feed()
                    once_mail = 1
                except Exception as e:
                    print("SW LED表示エラー:", repr(e))
                    once_mail = 1
            # BOOTSEL
            if bootSW() == 1:
                print("BOOTSELが押されたのでプログラム終了")
                safe_call("LED終了", lib_LED.end_LED)
                return
            time_stamp(12)
            now = time.localtime(time.time() + UTC_OFFSET)
            night = safe_call("夜間設定", config.nigth_mode, default=1)
            print("Time", now[3], ":", now[4], ".", now[5],
                  "温度:", temp, "湿度:", humi, "明暗:", cds_value,
                  "人感:", human, "SW:", SW, "wbgt:", wbgt, "night:", night)
            # 毎日5:50にNTP同期
            if now[3] == 5 and now[4] == 50 and now[7] != once_ntp_day:
                once_ntp_day = now[7]
                if main_py == 1:
                    safe_call("OLED再起動表示", SSD1306_m.OLED_mes, "reboot time")
                    machine.reset()
                wdt.feed()
                safe_call("NTP再同期", lib_NTP.NTP_set, wdt=wdt)
                wdt.feed()
                safe_call("OLED NTP表示", SSD1306_m.OLED_mes, "NTP")
                print("NTP")
            wdt.feed()
            gc.collect()
            wdt.feed()
            time_stamp(13)
            # 従来のループ周期を維持
            time.sleep(1)
            if night == 0:
                safe_call("LED点滅", lib_LED.LEDonoff)
            time_stamp(-1)
        except Exception as e:
            print("メインループエラー:", repr(e))
            led_off()
            try:
                wdt.feed()
            except Exception:
                pass
            time.sleep_ms(500)
# --------------------------------------------------
# プログラム起動
# --------------------------------------------------
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("main起動エラー:", repr(e))
        safe_call("OLEDエラー表示", SSD1306_m.OLED_mes, "main err")
        for i in range(10):
            if bootSW() == 1:
                safe_call("LED終了", lib_LED.end_LED)
                sys.exit()
            safe_call("LED点滅", lib_LED.LEDonoff)
            print("main-try:", i)
            safe_call("OLEDエラー表示", SSD1306_m.OLED_mes, "main-try:" + str(i))
            time.sleep_ms(500)
        if main_py == 1:
            time.sleep(10)
            safe_call("OLED再起動表示", SSD1306_m.OLED_mes, "reboot")
            machine.reset()
