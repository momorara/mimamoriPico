# -*- coding: utf-8 -*-
#!/usr/bin/python3
"""
ID PASS LINE_token
2023/5/7    lib化
2023/5/20   名称をconfig.pyとする
            測定周期を追加
2023/6/10   wifi 使用/不使用を追加
2023/6/19   補正値を持つ
v1.0
2023/8/25   mail活殺追加
2023/11/27  非表示設定
v04対応
2024/11/25  夜間LED点灯しない設定を追加
"""

def wifi_set():
    return 1 # wifi使用しない時は0

def ID_PASS():
    # wifiのssidとパスワード
    # あなたのwifiの設定に変更してください。
    ssid        = 'your ssid'
    password    = 'your password'
    return ssid,password

def mail_setting():
    mail_onoff = 1                              # SWのonでメールを送信するかどうかを設定
    MailServerName = "smtp.mail.yahoo.co.jp"    # メールサーバー名
    UserName = "coxxxsum@yahoo.co.jp"           # プロバイダーのアカウント(ユーザー名)
    UserPass = "yahxxx731"                      # プロバイダーのパスワード
    toMailAddres ="pc_xxxbox@mineo.jp"          # メールの宛先
    mail_title = "SW_test_ON"
    mail_body  = "SW_test_test"
    return mail_onoff,MailServerName,UserName,UserPass,toMailAddres,mail_title,mail_body
    
def hosei():
    # センサーのオフセット誤差を補正する補正値です。
    temp  = 0
    humdi = 0
    return temp,humdi

def ambi():
    # ambientのテストチャンネル ID,ライトキー
    # ご自身のambient設定に変更してください。
    ch_ID,write_KEY = 11111,"c1x5xx3283fxxcxxa3"
    return ch_ID,write_KEY 

def i2c_ini():
    # センサーとOLEDのi2cチャンネルとSDAのピン番号を設定
    i2c_no = 0
    SDA_pin= 0
    return i2c_no,SDA_pin

def measu_cycle():
    # 1分単位で計測周期を設定
    return 1

def Cds_ini():
    # Cdsで使うアナログ入力pinを設定
    # Cds値の範囲設定
    Cds_max = 60000
    Cds_min = 1500
    return 28,Cds_max,Cds_min

def hidden_setting():
    WBGT_hidden  = 25 # 25未満のWBGTはambient上非表示とする
    human_hidden = 5  # レベル3以下はambient上非表示とする
    return WBGT_hidden,human_hidden

# import datetime #micropythonでは使えない
import utime

def nigth_mode():
    # プログラムが面倒なので、昼間の点灯時間を設定します。
    Daytime_on = 5 # 朝のLED点灯開始時間
    Daytime_off = 23 # 夜間LED点灯時間の終わり Daytime_offはDaytime_onより大きい数字である事
    # dt_now = datetime.datetime.now()
    # 現在のUNIXタイムスタンプを取得 (UTC)
    current_time = utime.time()
    # 日本時間に変換 (+9時間 = 32400秒)
    jst_time = utime.localtime(current_time + 32400)
    # print( "hour",jst_time[3])
    nigth_mode = 1
    if jst_time[3] < Daytime_off and jst_time[3] >= Daytime_on:
        nigth_mode = 0
    #nigth_mode = 0 # 夜間LED消灯をする場合はこの行をコメントアウトする 
    return nigth_mode # この関数を使って戻り値が1ならLEDを点灯しない様にする

# 夜間設定のテスト用関数
def nigth_mode_test(i):
    # プログラムが面倒なので、昼間の点灯時間を設定します。
    Daytime_on = 5 # 朝のLED点灯開始時間
    Daytime_off = 22 # 夜間LED点灯時間の終わり Daytime_offはDaytime_onより大きい数字である事
    # dt_now = datetime.datetime.now()
    nigth_mode = 1
    if i < Daytime_off and i >= Daytime_on:
        nigth_mode = 0
    nigth_mode = 0 # 夜間LED消灯をする場合はこの行をコメントアウトする 
    return nigth_mode # この関数を使って戻り値が1ならLEDを点灯しない様にする

def main():
    print(wifi_set())
    print(ID_PASS())
    print(hosei())
    print(ambi())
    print(i2c_ini())
    print(measu_cycle())
    print(Cds_ini())
    print(mail_setting())
    print(nigth_mode())

    for i in range(24):
        print(i,nigth_mode_test(i))
    print(nigth_mode())

if __name__=='__main__':
    main()
