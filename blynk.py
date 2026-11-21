
"""
2026/11/17  wdtを使うので、
# ============================================================
# Blynk_PicoW.py
# Raspberry Pi Pico W / MicroPython v1.29.0
#
# Blynkデータ送信専用モジュール
#
# ・Blynk CloudへのHTTPS送信
# ・SSLソケットのタイムアウト対策
# ・通信エラー時はFalseを返す
# ・再試行なし
# ・WDT使用を考慮した短時間通信
#
# ============================================================
"""

import socket
import ssl
import time
import network
import config

# ------------------------------------------------------------
# 設定
# ------------------------------------------------------------

BLYNK_AUTH = config.BLYNK_token()

HOST = "blynk.cloud"
PORT = 443

# ソケットのタイムアウト（秒）
SOCKET_TIMEOUT = 2

# ------------------------------------------------------------
# HTTPレスポンスのステータス行を取得
# ------------------------------------------------------------

def read_status_line(sock):
    data = b""
    start = time.ticks_ms()

    while True:
        # 応答待ち時間の確認
        if time.ticks_diff(time.ticks_ms(), start) > 3000:
            raise OSError("HTTP応答タイムアウト")

        ch = sock.read(1)

        if not ch:
            break

        data += ch

        if ch == b"\n":
            break

        if len(data) > 128:
            raise OSError("HTTP応答データ異常")

    return data.decode().strip()

# ------------------------------------------------------------
# Blynkデータ送信
# ------------------------------------------------------------

def send_data(temp, humid, pressure, brightness, motion):

    if BLYNK_AUTH == "your token":
        print("Blynkトークン未設定")
        return False

    # Wi-Fi接続確認
    wlan = network.WLAN(network.STA_IF)

    if not wlan.isconnected():
        print("Wi-Fi未接続")
        return False

    sock = None

    try:
        # ----------------------------------------------------
        # URL作成
        # ----------------------------------------------------

        path = (
            "/external/api/batch/update"
            "?token=" + BLYNK_AUTH
            + "&V20=" + str(temp)
            + "&V21=" + str(humid)
            + "&V22=" + str(pressure)
            + "&V23=" + str(brightness)
            + "&V24=" + str(motion)
        )

        # ----------------------------------------------------
        # DNS検索
        # ----------------------------------------------------

        print("Blynk送信開始")

        addr = socket.getaddrinfo(HOST, PORT)[0][-1]

        # ----------------------------------------------------
        # TCPソケット作成
        # ----------------------------------------------------

        sock = socket.socket()

        # ★重要：SSL化する前にタイムアウトを設定
        sock.settimeout(SOCKET_TIMEOUT)

        # TCP接続
        sock.connect(addr)

        # ----------------------------------------------------
        # SSL化
        # ----------------------------------------------------

        sock = ssl.wrap_socket(
            sock,
            server_hostname=HOST
        )

        # ★SSL化した後はsettimeout()を呼ばない

        # ----------------------------------------------------
        # HTTPリクエスト送信
        # ----------------------------------------------------

        request = (
            "GET " + path + " HTTP/1.1\r\n"
            "Host: " + HOST + "\r\n"
            "Connection: close\r\n"
            "\r\n"
        )

        sock.write(request.encode())

        # ----------------------------------------------------
        # HTTPステータス取得
        # ----------------------------------------------------

        status_line = read_status_line(sock)

        print("HTTP応答:", status_line)

        # ----------------------------------------------------
        # 結果判定
        # ----------------------------------------------------

        parts = status_line.split()

        if len(parts) >= 2:
            status = int(parts[1])

            if status == 200:
                print("Blynk送信成功")
                return True

            print("Blynk HTTPエラー:", status)
            return False

        print("HTTP応答形式エラー")
        return False

    except Exception as e:
        print("Blynk通信エラー:", repr(e))
        return False

    finally:
        # ----------------------------------------------------
        # ソケットを必ず閉じる
        # ----------------------------------------------------

        if sock is not None:
            try:
                sock.close()
            except Exception:
                pass

        print("Blynk送信処理終了")

# ------------------------------------------------------------
# 単独動作テスト
# ------------------------------------------------------------

if __name__ == "__main__":

    print("Blynk送信テスト")

    result = send_data(
        25.5,   # 温度
        60,     # 湿度
        1013,   # 気圧
        80,     # 照度
        1       # 動体
    )

    print("送信結果:", result)


def main():
    import random
    import wifi_connect
    import lib_NTP

    wifi_connect.connect()
    lib_NTP.NTP_set()
    # メインループ
    while True:
        try:
            # 次の正分まで待つ
            now = time.localtime()
            wait_sec = 60 - now[5]
            print("次の正分まで待つ",wait_sec,"秒")
            time.sleep(wait_sec)

            # 毎正分に送信処理を開始
            print("送信開始:", time.localtime())

            # センサー読み取り
            # temp, humid, pressure, brightness, motion, switch = (read_sensors())
            temp, humid, pressure, brightness, motion = 25.1 + random.randint(1, 5),40 + random.randint(1, 30),999+ random.randint(1, 30),50 + random.randint(1, 30),random.randint(1, 10)
            print(temp, humid, pressure,brightness, motion)

            wifi_connect.keep_alive()

            start_time = time.time()
            # Blynkへ送信
            send_data(temp, humid, pressure,brightness, motion)
            elapsed_time = time.time() - start_time

            print("処理時間: {:.4f} 秒".format(elapsed_time))

        except Exception as e:
            print("処理エラー:", e)
        print("-----------------")

if __name__=='__main__':
    main()
