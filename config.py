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
    toMailAddres ="nobxx21@me.com"              # メールの宛先
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
    ch_ID,write_KEY = 45678,"c1x5xx3283fxxcxxa3"
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

def main():
    print(wifi_set())
    print(ID_PASS())
    print(hosei())
    print(ambi())
    print(i2c_ini())
    print(measu_cycle())
    print(Cds_ini())
    print(mail_setting())

if __name__=='__main__':
    main()
