# -*- coding: utf-8 -*-
#!/usr/bin/python3
"""
2023/5/8    lib化
            キャリブレーション方法
            このプログラムを起動
            0:オリジナルデータが見える
            最大明るい、最大暗い時のデータをCds max,minに代入する。
2023/05/21  設定値をconfig.pyから取得
v1.0
"""

# -*- coding: utf-8 -*-
# ==================================================
# lib_Cds.py
# Raspberry Pi Pico W / MicroPython
# CDSセンサー読み取り
# v1.1 2026/11/18
# ==================================================
from machine import ADC, Pin
import time
import config
# --------------------------------------------------
# CDS設定
# --------------------------------------------------
try:
    analog_pin, Cds_max, Cds_min = config.Cds_ini()
    Cds_max = int(Cds_max)
    Cds_min = int(Cds_min)
    if not 0 <= analog_pin <= 29:
        raise ValueError("ADCピン番号エラー")
    if not 0 <= Cds_min < Cds_max <= 65535:
        raise ValueError("CDS校正値エラー")
    adc = ADC(Pin(analog_pin))
except Exception as e:
    print("CDS初期化エラー:", repr(e))
    adc = None
    Cds_max = 60000
    Cds_min = 1500
# --------------------------------------------------
# CDS読み取り
# --------------------------------------------------
def Cds(flag):
    if adc is None:
        return 0
    try:
        analog_value_org = adc.read_u16()
        analog_value = max(Cds_min, min(analog_value_org, Cds_max))
        analog_100 = int((analog_value - Cds_min) * 100 / (Cds_max - Cds_min))
        analog_100 = max(0, min(analog_100, 100))
        if flag == 0:
            print("Analog Value:", analog_value_org, analog_value, analog_100)
        return analog_100
    except Exception as e:
        print("CDS読み取りエラー:", repr(e))
        return 0
# --------------------------------------------------
# 単独実行テスト
# --------------------------------------------------
def main():
    for i in range(5):
        print(Cds(0))
        time.sleep(1)
if __name__ == "__main__":
    main()
