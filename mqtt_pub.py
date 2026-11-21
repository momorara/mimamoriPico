# 2024/8/22
"""
トピックとデータを引数にmqtt_sendを実行すると
指定されたプローカーに対にしてパブリッシュします。
2024/08/24  mqttのコアプログラムの名前を変え、インストールしやすいようにした
2025/02/02  mqttのプローカーを変更
            mqtt送信タイミングを乱数でずらす
2026/11/17  wdtを使うので、タイミングは使用しない
"""

import network
import time
import ubinascii
import machine
from lib_mqtt import MQTTClient

# MQTTブローカー情報
broker = 'broker.hivemq.com'
client_id = ubinascii.hexlify(machine.unique_id())
print("Client ID:", client_id)

# Wi-Fiは接続済みとして扱う
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    return wlan.isconnected()

# MQTT接続
def connect_mqtt():
    client = MQTTClient(
        client_id,
        broker,
        port=1883,
        timeout=5,
        keepalive=120
    )
    client.connect()
    print('MQTTに接続完了')
    return client

# MQTT送信
def mqtt_send(topic, data):
    client = None
    connected = False

    print("送信:", topic, data)

    try:
        # Wi-Fi接続確認
        if not connect_wifi():
            print("Wi-Fi未接続")
            return False

        # MQTT接続
        client = connect_mqtt()
        connected = True

        # メッセージ送信
        client.publish(topic, str(data))
        print("送信成功:", data)
        return True

    except Exception as e:
        print("MQTT通信エラー:", repr(e))
        return False

    finally:
        if client is not None:
            if connected:
                try:
                    client.disconnect()
                    print("MQTT接続を終了しました")
                except Exception as e:
                    print("切断エラー:", repr(e))
                    try:
                        client.sock.close()
                    except:
                        pass
            else:
                # 接続途中で失敗した場合
                try:
                    if client.sock is not None:
                        client.sock.close()
                except:
                    pass

def main():
    while True:
        topic = "tkj/raspberry_pico/temp_AHT/46"
        data = 31

        start_time = time.ticks_ms()
        result = mqtt_send(topic, data)
        elapsed_time = time.ticks_ms() - start_time

        elapsed_time = time.ticks_diff(time.ticks_ms(), start_time)
        print("処理時間:", elapsed_time, "ms")

        time.sleep(10)

if __name__ == '__main__':
    main()


