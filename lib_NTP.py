# -*- coding: utf-8 -*-
#!/usr/bin/python3
"""
2023/05/21  NTPにて時刻あわせ
v1.0
2026/08/24  日本国内のNTPサーバーに変更
v1.1
"""

# -*- coding: utf-8 -*-
# ==================================================
# lib_NTP.py
# Raspberry Pi Pico W / MicroPython
# NTP時刻取得・タイムアウト対策版
# v1.2 2026/11/18
# ==================================================
import time
import ntptime
# --------------------------------------------------
# NTP設定
# --------------------------------------------------
NTP_HOST = "ntp.nict.jp"
UTC_OFFSET = 9 * 60 * 60
MAX_RETRY = 2
RETRY_WAIT = 0.5
TIMEOUT = 2
# --------------------------------------------------
# NTP時刻設定
# --------------------------------------------------
def NTP_set():
    ntptime.host = NTP_HOST
    # NTPモジュールのタイムアウト設定
    if hasattr(ntptime, "timeout"):
        ntptime.timeout = TIMEOUT
    for retry in range(MAX_RETRY):
        try:
            print("NTP: 時刻取得開始", retry + 1, "/", MAX_RETRY)
            ntptime.settime()
            # 取得結果確認
            now = time.time()
            if now < 1700000000:
                raise OSError("NTP時刻が不正です")
            local_date_time = time.localtime(now + UTC_OFFSET)
            print("NTP: 時刻取得成功")
            print(local_date_time)
            return True
        except Exception as e:
            print("NTPエラー:", repr(e))
            if retry < MAX_RETRY - 1:
                time.sleep(RETRY_WAIT)
    print("NTP: 時刻取得失敗")
    return False


def main():
    while True:
        NTP_set()
        time.sleep(3)

if __name__=='__main__':
    main()