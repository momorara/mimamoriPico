
"""
2026/11/17  wdtを使うので、
項目	修正
SSL化前	settimeout(2) を設定
SSL化後	settimeout() を一切使用しない
HTTP 429	待機せずFalseを返す
通信エラー	Falseを返す
再試行	なし
通信後	ソケットを閉じる
"""

import time
import socket
import ssl
import json
import config

# --------------------------------------------------
# MiniViz設定
# --------------------------------------------------

TOKEN, PROJECT_ID, LABEL_KEY = config.MINIVIZ_token()

HOST = "api.miniviz.net"

PATH = "/api/project/{}?token={}".format(
    PROJECT_ID, TOKEN
)

SEND_TIMEOUT = 6000       # 全体の目標制限時間(ms)
SOCKET_TIMEOUT = 2        # SSL化前のソケット待ち時間(秒)


# --------------------------------------------------
# MiniVizデータ送信
# --------------------------------------------------

def send_data(temperature, humidity, pressure, brightness, motion):

    if TOKEN == "your token":
        print("MiniVizトークン未設定")
        return False

    start = time.ticks_ms()
    sock = None

    try:
        # 送信データ作成
        timestamp_ms = int(time.time() * 1000)

        payload = {
            "timestamp": timestamp_ms,
            "label_key": LABEL_KEY,
            "payload": {
                "temperature": temperature,
                "humidity": humidity,
                "pressure": pressure,
                "brightness": brightness,
                "motion": motion
            }
        }

        body = json.dumps(payload)

        # HTTPリクエスト作成
        body_bytes = body.encode()

        request = (
            "POST " + PATH + " HTTP/1.1\r\n"
            "Host: " + HOST + "\r\n"
            "Content-Type: application/json\r\n"
            "Content-Length: " + str(len(body_bytes)) + "\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).encode() + body_bytes

        print("MiniViz送信開始")

        # DNS名前解決
        addr = socket.getaddrinfo(HOST, 443)[0][-1]

        # ソケット作成
        sock = socket.socket()

        # ★SSL化する前にタイムアウトを設定
        sock.settimeout(SOCKET_TIMEOUT)

        # HTTPS接続
        sock.connect(addr)

        # SSL化
        sock = ssl.wrap_socket(
            sock,
            server_hostname=HOST
        )

        # ★SSL化した後はsettimeout()を使用しない

        # 送信時間確認
        if time.ticks_diff(time.ticks_ms(), start) >= SEND_TIMEOUT:
            raise OSError("送信タイムアウト")

        # HTTPリクエスト送信
        sock.write(request)

        # HTTPヘッダー受信
        response = b""

        while b"\r\n\r\n" not in response:

            elapsed = time.ticks_diff(time.ticks_ms(), start)

            if elapsed >= SEND_TIMEOUT:
                raise OSError("送信タイムアウト")

            # SSLソケットではsettimeout()を呼ばない
            data = sock.read(256)

            if not data:
                break

            response += data

            if len(response) > 4096:
                raise OSError("HTTPヘッダーサイズ超過")

        # HTTPステータス確認
        if b"\r\n" not in response:
            raise OSError("HTTP応答なし")

        status_line = response.split(b"\r\n", 1)[0]

        print("HTTP Status:", status_line)

        # 成功
        if b" 200 " in status_line or b" 201 " in status_line:
            print("MiniViz送信成功")
            return True

        # HTTP 429
        if b" 429 " in status_line:
            print("HTTP 429: アクセス制限")
            return False

        print("MiniViz送信失敗")
        return False

    except Exception as e:
        print("MiniViz通信エラー:", repr(e))
        return False

    finally:

        if sock is not None:
            try:
                sock.close()
            except:
                pass

        elapsed = time.ticks_diff(time.ticks_ms(), start)

        print("MiniViz処理時間:", elapsed, "ms")


# --------------------------------------------------
# 単独実行時のテスト
# --------------------------------------------------

def main():
    import random
    import wifi_connect

    print("")
    print("================================")
    print("MiniViz データ送信テスト")
    print("================================")

    print("Project ID:", PROJECT_ID)
    print("Label Key:", LABEL_KEY)

    wifi_connect.connect()

    while True:
        try:
            # センサー読み取り
            # temp, humid, pressure, brightness, motion, switch = (read_sensors())
            temp, humid, pressure, brightness, motion = 25.1 + random.randint(1, 5),40 + random.randint(1, 30),999+ random.randint(1, 30),50 + random.randint(1, 30),random.randint(1, 10)
            print(temp, humid, pressure,brightness, motion)

            wifi_connect.keep_alive()

            start_time = time.time()
            result = send_data(temp, humid, pressure, brightness, motion)
            elapsed_time = time.time() - start_time

            print("今回の送信:", "OK" if result else "NG")
            print("処理時間: {:.4f} 秒".format(elapsed_time))

        except Exception as e:
            print("処理エラー:", e)
            
        print("--------------------")
        time.sleep(60)
# --------------------------------------------------
# プログラム開始
# --------------------------------------------------

if __name__ == "__main__":
    main()

