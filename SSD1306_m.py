"""
2023/05/10
2023/05/21	OLED 焼き付け防止
v1.0
2023/08/22  mimamori用に改造
"""
import time
from machine import Pin, I2C
import ssd1306
import config
import random


def OLED(CPU_temp,Cds,human,SW=0):
    try:
        i2c_no,SDA_pin = config.i2c_ini()
        # I2Cバスを設定
        i2c = I2C(i2c_no, sda=Pin(SDA_pin) ,scl=Pin(SDA_pin+1))
        # OLEDディスプレイの設定
        try:
            oled = ssd1306.SSD1306_I2C(128, 32, i2c)
        except:
            pass

        # OLEDディスプレイをクリア
        oled.fill(0)
        
        sp = ' '
        if CPU_temp < 10 :sp = sp + ' '
        temp_s  = 'temp  = ' + sp + str(CPU_temp) 

        if Cds  != 100:
            if Cds < 10:
                Cds_s = 'Cds    =  ' + str(Cds)
            else:
                Cds_s = 'Cds   =  '  + str(Cds)
        else:
                Cds_s = 'Cds   =  100.0 '
                
        sw_s =" sw:off"        
        if SW > 0:sw_s =" sw:on"
        
        human_s = 'human:' + str(human) + sw_s

        set_x = random.randint(0,17)
        set_y = random.randint(0, 1)
        set_z = random.randint(0, 1)
        # テキストを描画
        oled.text(temp_s,  set_x, set_y + 0   + set_z)
        oled.text(Cds_s, set_x, set_y + 12  - set_z)
        oled.text(human_s, set_x, set_y + 24  - set_z *2)

        # 変更を表示
        oled.show()
    except:
        pass   

def OLED_mes(mes):
    try:
        i2c_no,SDA_pin = config.i2c_ini()
        # I2Cバスを設定
        i2c = I2C(i2c_no, sda=Pin(SDA_pin) ,scl=Pin(SDA_pin+1))
        # OLEDディスプレイの設定
        try:
            oled = ssd1306.SSD1306_I2C(128, 32, i2c)
        except:
            pass
        # OLEDディスプレイをクリア
        oled.fill(0)
        # メッセージを書き込み
        oled.text(mes,  5, 12)
        # 変更を表示
        oled.show()
    except:
        pass


def main():
    temp,humdy,press,sw = 24.8,88,1,0
    OLED(temp,humdy,press,sw)
    time.sleep(5)
    OLED_mes("test")
    time.sleep(3)
    OLED_mes("")

if __name__=='__main__':
    main()

