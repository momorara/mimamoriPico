"""
2023/05/10
2023/05/21	OLED 焼き付け防止
v1.0
2023/08/22  mimamori用に改造
"""

# ==================================================
# SSD1306 OLED表示プログラム
# Raspberry Pi Pico W / MicroPython
#
# 2026/11/17 改良版
#
# ・OLED初期化は原則1回
# ・I2C通信エラー対策
# ・異常時は次回呼び出しで再初期化
# ・焼き付き防止の表示位置ランダム移動
# ・OLED / OLED_mes 両対応
# ・通信タイムアウト設定
# ==================================================

import time
import random
from machine import Pin, I2C
import ssd1306
import config

# --------------------------------------------------
# 設定
# --------------------------------------------------
OLED_WIDTH = 128
OLED_HEIGHT = 32
I2C_FREQ = 400_000
I2C_TIMEOUT = 100_000  # マイクロ秒（100ms）
OLED_ADDRESS = 0x3C

# --------------------------------------------------
# グローバル変数
# --------------------------------------------------
_oled = None
_i2c = None
_i2c_config = None

# --------------------------------------------------
# OLED初期化
# --------------------------------------------------
def OLED_init():
    global _oled, _i2c, _i2c_config
    try:
        i2c_no, SDA_pin = config.i2c_ini()
        current_config = (i2c_no, SDA_pin)
        # 初回または設定変更時のみI2Cを生成
        if _i2c is None or _i2c_config != current_config:
            _oled = None
            _i2c = None
            _i2c = I2C(
                i2c_no,
                sda=Pin(SDA_pin),
                scl=Pin(SDA_pin + 1),
                freq=I2C_FREQ,
                timeout=I2C_TIMEOUT
            )
            _i2c_config = current_config
        # OLED初期化
        if _oled is None:
            _oled = ssd1306.SSD1306_I2C(
                OLED_WIDTH,
                OLED_HEIGHT,
                _i2c,
                addr=OLED_ADDRESS
            )
        return _oled
    except Exception as e:
        _oled = None
        _i2c = None
        _i2c_config = None
        print("OLED初期化エラー:", e)
        return None

# --------------------------------------------------
# 通信エラー処理
# --------------------------------------------------
def OLED_error(e):
    global _oled, _i2c, _i2c_config
    print("OLED通信エラー:", e)
    # 次回呼び出し時に再初期化
    _oled = None
    _i2c = None
    _i2c_config = None
    return False

# --------------------------------------------------
# 温度・照度・人感・スイッチ表示
# --------------------------------------------------
def OLED(CPU_temp, Cds, human, SW=0):
    try:
        oled = OLED_init()
        if oled is None:
            return False
        # 表示データ作成
        sp = ' '
        if CPU_temp < 10:
            sp += ' '
        temp_s = 'temp  = ' + sp + str(CPU_temp)
        if Cds != 100:
            if Cds < 10:
                Cds_s = 'Cds    =  ' + str(Cds)
            else:
                Cds_s = 'Cds   =  ' + str(Cds)
        else:
            Cds_s = 'Cds   =  100.0 '
        sw_s = " sw:off"
        if SW > 0:
            sw_s = " sw:on"
        human_s = 'human:' + str(human) + sw_s
        # 焼き付き防止のため表示位置をランダムに移動
        set_x = random.randint(0, 17)
        set_y = random.randint(0, 1)
        set_z = random.randint(0, 1)
        # OLED表示
        oled.fill(0)
        oled.text(temp_s, set_x, set_y + set_z)
        oled.text(Cds_s, set_x, set_y + 12 - set_z)
        oled.text(human_s, set_x, set_y + 24 - set_z * 2)
        oled.show()
        return True
    except Exception as e:
        return OLED_error(e)

# --------------------------------------------------
# メッセージ表示
# --------------------------------------------------
def OLED_mes(mes):
    try:
        oled = OLED_init()
        if oled is None:
            return False
        oled.fill(0)
        oled.text(str(mes), 5, 12)
        oled.show()
        return True
    except Exception as e:
        return OLED_error(e)

# --------------------------------------------------
# 単独動作テスト
# --------------------------------------------------
def main():
    temp, humdy, press, sw = 24.8, 88, 1, 0
    if OLED(temp, humdy, press, sw):
        time.sleep(5)
    OLED_mes("test")
    time.sleep(3)
    OLED_mes("")

# --------------------------------------------------
# メイン
# --------------------------------------------------
if __name__ == "__main__":
    main()
