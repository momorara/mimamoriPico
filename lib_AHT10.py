#!/usr/bin/env python
# -*- coding: utf-8 -*-
# https://www.route55go.com/self-study/pico/class/s006_ath10/
# AHT10 Library for MicroPython on ESP32
# Author: Sean Yong
# Date: 23rd December, 2019
# Version 1.0
# pico W 用に改造 2023/5/10

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AHT10 温度・湿度センサーライブラリ
Raspberry Pi Pico W / MicroPython

改善内容
・I2C通信エラー対策
・センサー初期化エラー対策
・測定データの異常チェック
・通信再試行（最大2回）
・温度、湿度を同時取得
・5秒以内の処理を目標に制限
・既存の補正機能を維持

"""

import time
from machine import I2C, Pin
import config

# --------------------------------------------------
# 設定
# --------------------------------------------------

T_hosei, H_hosei, press = config.hosei()
i2c_no, SDA_pin = config.i2c_ini()

AHT10_ADDRESS = 0x38

AHT10_READ_DELAY_MS = 80
AHT10_TIMEOUT_MS = 500

CMD_INITIALIZE = b'\xE1\x08\x00'
CMD_MEASURE = b'\xAC\x33\x00'

MAX_RETRY = 2

# --------------------------------------------------
# AHT10クラス
# --------------------------------------------------

class AHT10:

    def __init__(self, i2c01, sda_pin, mode=0,
                 address=AHT10_ADDRESS):

        self.address = address
        self.mode = mode

        self.i2c = I2C(
            i2c01,
            scl=Pin(sda_pin + 1),
            sda=Pin(sda_pin),
            freq=400_000
        )

        self.readings_raw = bytearray(6)
        self.results_parsed = [0, 0]

        self.initialized = False

        self.initialize()

    # --------------------------------------------------
    # センサー初期化
    # --------------------------------------------------

    def initialize(self):

        try:
            self.i2c.writeto(
                self.address,
                CMD_INITIALIZE
            )

            time.sleep_ms(20)

            self.initialized = True
            return True

        except Exception as e:

            self.initialized = False
            print("AHT10初期化エラー:", e)

            return False

    # --------------------------------------------------
    # 温度・湿度の生データ取得
    # --------------------------------------------------

    def read_raw(self):

        for retry in range(MAX_RETRY):

            try:

                if not self.initialized:
                    if not self.initialize():
                        continue

                self.i2c.writeto(
                    self.address,
                    CMD_MEASURE
                )

                time.sleep_ms(AHT10_READ_DELAY_MS)

                # センサー応答確認
                start = time.ticks_ms()

                while True:

                    self.i2c.readfrom_into(
                        self.address,
                        self.readings_raw
                    )

                    # bit7 = 0なら測定完了
                    if not (self.readings_raw[0] & 0x80):
                        break

                    if time.ticks_diff(
                        time.ticks_ms(), start
                    ) > AHT10_TIMEOUT_MS:
                        raise OSError("AHT10測定タイムアウト")

                    time.sleep_ms(10)

                # キャリブレーション状態確認
                if not (self.readings_raw[0] & 0x08):
                    raise OSError("AHT10未校正")

                # 湿度データ
                humidity_raw = (
                    (self.readings_raw[1] << 12)
                    | (self.readings_raw[2] << 4)
                    | (self.readings_raw[3] >> 4)
                )

                # 温度データ
                temperature_raw = (
                    ((self.readings_raw[3] & 0x0F) << 16)
                    | (self.readings_raw[4] << 8)
                    | self.readings_raw[5]
                )

                # 湿度・温度変換
                humidity = humidity_raw * 100 / 1048576

                temperature = (
                    temperature_raw * 200 / 1048576
                ) - 50

                # 異常値チェック
                if not (0 <= humidity <= 100):
                    raise ValueError("湿度異常")

                if not (-40 <= temperature <= 85):
                    raise ValueError("温度異常")

                self.results_parsed[0] = humidity_raw
                self.results_parsed[1] = temperature_raw

                return temperature, humidity

            except Exception as e:

                self.initialized = False

                if retry == MAX_RETRY - 1:
                    raise OSError(
                        "AHT10読み取り失敗: {}".format(e)
                    )

                time.sleep_ms(50)

        raise OSError("AHT10通信失敗")

    # --------------------------------------------------
    # 湿度
    # --------------------------------------------------

    def humidity(self):

        _, humidity = self.read_raw()
        return humidity

    # --------------------------------------------------
    # 温度
    # --------------------------------------------------

    def temperature(self):

        temperature, _ = self.read_raw()

        if self.mode == 1:
            temperature = temperature * 9 / 5 + 32

        return temperature

    # --------------------------------------------------
    # 温度・湿度同時取得
    # --------------------------------------------------

    def read(self):

        return self.read_raw()

    # --------------------------------------------------
    # モード設定
    # --------------------------------------------------

    def set_mode(self, mode):

        if mode not in (0, 1):
            raise ValueError(
                "Mode must be 0(Celsius) or 1(Fahrenheit)"
            )

        self.mode = mode

    # --------------------------------------------------
    # 表示
    # --------------------------------------------------

    def print(self):

        temperature, humidity = self.read()

        unit = "C" if self.mode == 0 else "F"

        if self.mode == 1:
            temperature = temperature * 9 / 5 + 32

        print(
            "Temperature:",
            temperature, unit,
            "Humidity:", humidity
        )


# --------------------------------------------------
# インスタンス生成
# --------------------------------------------------

aht = AHT10(i2c_no, SDA_pin, 0)


# --------------------------------------------------
# 従来の呼び出し関数
# --------------------------------------------------

def aht10(flag):

    # 温度・湿度を1回の測定で取得
    temp, humi = aht.read()

    # 表示
    if flag == 0:
        print("Temp=", temp, " RH%=", humi)

    # 小数点以下1桁に丸めて補正
    temp = int(temp * 10 + 0.1) / 10 + T_hosei
    humi = int(humi * 10 + 0.1) / 10 + H_hosei

    return temp, humi


# --------------------------------------------------
# 単独実行テスト
# --------------------------------------------------

def main():

    for i in range(4):

        try:

            temp, humi = aht10(1)

            print(
                "Temp=", temp,
                " RH%=", humi
            )

        except Exception as e:

            print("センサーエラー:", e)

        time.sleep(1)


if __name__ == "__main__":
    main()
