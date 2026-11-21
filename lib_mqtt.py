"""
オリジナルは
https://github.com/micropython/micropython-lib/blob/master/micropython/umqtt.simple/umqtt/simple.py
にあります。
プログラム名以外は変更していません。
"""

# ==================================================
# lib_mqtt.py
# MQTTClient タイムアウト対応版
# Raspberry Pi Pico W / MicroPython
# ==================================================

import socket
import struct
import time
class MQTTException(Exception):
    pass
class MQTTClient:
    def __init__(self, client_id, server, port=0, user=None, password=None, keepalive=0, ssl=None, timeout=5):
        if port == 0:
            port = 8883 if ssl else 1883
        self.client_id = client_id
        self.sock = None
        self.server = server
        self.port = port
        self.ssl = ssl
        self.pid = 0
        self.cb = None
        self.user = user
        self.pswd = password
        self.keepalive = keepalive
        self.lw_topic = None
        self.lw_msg = None
        self.lw_qos = 0
        self.lw_retain = False
        self.timeout = max(0.1, min(float(timeout), 5.0))
        self._deadline = None
    # --------------------------------------------------
    # 処理期限管理
    # --------------------------------------------------
    def _start_timer(self):
        self._deadline = time.ticks_add(time.ticks_ms(), 5000)
    def _remaining(self):
        if self._deadline is None:
            return self.timeout
        remaining = time.ticks_diff(self._deadline, time.ticks_ms()) / 1000
        if remaining <= 0:
            raise OSError("MQTT処理タイムアウト")
        return min(remaining, self.timeout)
    # --------------------------------------------------
    # ソケットタイムアウト設定
    # --------------------------------------------------
    def _set_timeout(self, timeout=None):
        if self.sock is None:
            raise OSError("MQTT未接続")
        t = self._remaining() if timeout is None else min(timeout, self._remaining())
        try:
            self.sock.settimeout(max(0.05, t))
        except Exception:
            pass
    # --------------------------------------------------
    # ソケット終了
    # --------------------------------------------------
    def close(self):
        s = self.sock
        self.sock = None
        if s is not None:
            try:
                s.close()
            except Exception:
                pass
    # --------------------------------------------------
    # 送信処理
    # --------------------------------------------------
    def _write_all(self, data):
        if self.sock is None:
            raise OSError("MQTT未接続")
        pos = 0
        while pos < len(data):
            self._set_timeout()
            n = self.sock.write(data[pos:])
            if n is None or n <= 0:
                raise OSError("MQTT送信エラー")
            pos += n
    def _send_str(self, s):
        if isinstance(s, str):
            s = s.encode()
        if len(s) > 65535:
            raise MQTTException("文字列サイズエラー")
        self._write_all(struct.pack("!H", len(s)))
        self._write_all(s)
    # --------------------------------------------------
    # 指定サイズ受信
    # --------------------------------------------------
    def _read_exact(self, size):
        if size < 0 or size > 268435455:
            raise MQTTException("受信サイズエラー")
        data = bytearray()
        while len(data) < size:
            self._set_timeout()
            part = self.sock.read(size - len(data))
            if not part:
                raise OSError("MQTT受信切断")
            data.extend(part)
        return bytes(data)
    # --------------------------------------------------
    # MQTTパケット長
    # --------------------------------------------------
    def _encode_len(self, size):
        if size < 0 or size > 268435455:
            raise MQTTException("MQTTパケット長エラー")
        result = bytearray()
        while True:
            digit = size & 0x7F
            size >>= 7
            if size:
                digit |= 0x80
            result.append(digit)
            if not size:
                break
        return bytes(result)
    def _recv_len(self):
        n = 0
        multiplier = 1
        for _ in range(4):
            b = self._read_exact(1)[0]
            n += (b & 0x7F) * multiplier
            if not b & 0x80:
                return n
            multiplier *= 128
        raise MQTTException("MQTTパケット長エラー")
    # --------------------------------------------------
    # コールバック
    # --------------------------------------------------
    def set_callback(self, f):
        self.cb = f
    def set_last_will(self, topic, msg, retain=False, qos=0):
        if not 0 <= qos <= 2 or not topic:
            raise ValueError("Last Will設定エラー")
        self.lw_topic = topic
        self.lw_msg = msg
        self.lw_qos = qos
        self.lw_retain = retain
    # --------------------------------------------------
    # MQTT接続
    # --------------------------------------------------
    def connect(self, clean_session=True):
        self.close()
        self._start_timer()
        try:
            print("MQTT: DNS検索開始")
            addr = socket.getaddrinfo(self.server, self.port)[0][-1]
            self._remaining()
            print("MQTT: DNS検索成功")
            self.sock = socket.socket()
            self._set_timeout()
            print("MQTT: TCP接続開始")
            self.sock.connect(addr)
            self._remaining()
            print("MQTT: TCP接続成功")
            if self.ssl:
                print("MQTT: SSL接続開始")
                self.sock = self.ssl.wrap_socket(self.sock, server_hostname=self.server)
                self._remaining()
                print("MQTT: SSL接続成功")
            # CONNECTフラグ
            flags = (int(bool(clean_session)) << 1)
            if self.user is not None:
                flags |= 0x80
                if self.pswd is not None:
                    flags |= 0x40
            if self.lw_topic is not None:
                flags |= 0x04 | (self.lw_qos << 3)
                if self.lw_retain:
                    flags |= 0x20
            # CONNECTデータ作成
            msg = bytearray(b"\x00\x04MQTT\x04")
            msg.append(flags)
            msg.extend(struct.pack("!H", self.keepalive))
            msg.extend(struct.pack("!H", len(self.client_id.encode() if isinstance(self.client_id, str) else self.client_id)))
            msg.extend(self.client_id.encode() if isinstance(self.client_id, str) else self.client_id)
            if self.lw_topic is not None:
                topic = self.lw_topic.encode() if isinstance(self.lw_topic, str) else self.lw_topic
                will = self.lw_msg.encode() if isinstance(self.lw_msg, str) else self.lw_msg
                msg.extend(struct.pack("!H", len(topic)))
                msg.extend(topic)
                msg.extend(struct.pack("!H", len(will)))
                msg.extend(will)
            if self.user is not None:
                self._append_string(msg, self.user)
                if self.pswd is not None:
                    self._append_string(msg, self.pswd)
            packet = b"\x10" + self._encode_len(len(msg)) + bytes(msg)
            print("MQTT: CONNECT送信")
            self._write_all(packet)
            print("MQTT: CONNACK応答待ち")
            resp = self._read_exact(4)
            print("MQTT: CONNACK受信", resp)
            if resp[0] != 0x20 or resp[1] != 0x02:
                raise MQTTException("MQTT接続応答エラー")
            if resp[3] != 0:
                raise MQTTException("MQTT接続拒否: {}".format(resp[3]))
            print("MQTT: 接続成功")
            return resp[2] & 1
        except Exception as e:
            print("MQTT接続エラー:", repr(e))
            self.close()
            raise
        finally:
            self._deadline = None
    def _append_string(self, buf, value):
        if isinstance(value, str):
            value = value.encode()
        if len(value) > 65535:
            raise MQTTException("文字列サイズエラー")
        buf.extend(struct.pack("!H", len(value)))
        buf.extend(value)
    # --------------------------------------------------
    # MQTT切断
    # --------------------------------------------------
    def disconnect(self):
        try:
            if self.sock is not None:
                self._start_timer()
                self._write_all(b"\xe0\x00")
        except Exception as e:
            print("MQTT切断処理:", repr(e))
        finally:
            self._deadline = None
            self.close()
    # --------------------------------------------------
    # PING
    # --------------------------------------------------
    def ping(self):
        self._start_timer()
        try:
            self._write_all(b"\xc0\x00")
        except Exception:
            self.close()
            raise
        finally:
            self._deadline = None
    # --------------------------------------------------
    # MQTT送信
    # --------------------------------------------------
    def publish(self, topic, msg, retain=False, qos=0):
        if qos not in (0, 1):
            raise MQTTException("QoS 2未対応")
        if self.sock is None:
            raise OSError("MQTT未接続")
        if isinstance(topic, str):
            topic = topic.encode()
        if isinstance(msg, str):
            msg = msg.encode()
        if len(topic) > 65535:
            raise MQTTException("トピックサイズエラー")
        self._start_timer()
        try:
            self.pid = (self.pid % 65535) + 1
            header = 0x30 | (qos << 1) | int(bool(retain))
            size = 2 + len(topic) + len(msg) + (2 if qos else 0)
            packet = bytes([header]) + self._encode_len(size)
            self._write_all(packet)
            self._send_str(topic)
            if qos:
                self._write_all(struct.pack("!H", self.pid))
            self._write_all(msg)
            if qos == 1:
                while True:
                    op = self.wait_msg()
                    if op == 0x40:
                        length = self._recv_len()
                        if length != 2:
                            raise MQTTException("PUBACKエラー")
                        rcv_pid = struct.unpack("!H", self._read_exact(4))[0]
                        if rcv_pid == self.pid:
                            return
        except Exception as e:
            print("MQTT送信エラー:", repr(e))
            self.close()
            raise
        finally:
            self._deadline = None
    # --------------------------------------------------
    # MQTT受信
    # --------------------------------------------------
    def _wait_msg(self, first):
        op = first[0]
        if op == 0xD0:
            if self._recv_len() != 0:
                raise MQTTException("PINGRESPエラー")
            return None
        if op & 0xF0 != 0x30:
            return op
        sz = self._recv_len()
        if sz < 2:
            raise MQTTException("PUBLISHパケットエラー")
        topic_len = struct.unpack("!H", self._read_exact(4))[0]
        if topic_len > sz - 2:
            raise MQTTException("トピック長エラー")
        topic = self._read_exact(topic_len)
        sz -= topic_len + 2
        qos = (op >> 1) & 3
        if qos == 3:
            raise MQTTException("QoSエラー")
        pid = None
        if qos:
            if sz < 2:
                raise MQTTException("パケットIDエラー")
            pid = struct.unpack("!H", self._read_exact(4))[0]
            sz -= 2
        msg = self._read_exact(sz)
        if self.cb:
            self.cb(topic, msg)
        if qos == 1:
            self._write_all(b"\x40\x02" + struct.pack("!H", pid))
        elif qos == 2:
            raise MQTTException("QoS 2未対応")
        return op
    def wait_msg(self):
        if self.sock is None:
            raise OSError("MQTT未接続")
        self._start_timer()
        try:
            self._set_timeout()
            res = self.sock.read(1)
            if res is None:
                return None
            if res == b"":
                raise OSError("MQTT切断")
            return self._wait_msg(res)
        except Exception as e:
            print("MQTT受信エラー:", repr(e))
            self.close()
            raise
        finally:
            self._deadline = None
    # --------------------------------------------------
    # メッセージ確認（データがなければ待たない）
    # --------------------------------------------------
    def check_msg(self):
        if self.sock is None:
            raise OSError("MQTT未接続")
        self._start_timer()
        try:
            self.sock.setblocking(False)
            res = self.sock.read(1)
            if res is None:
                return None
            if res == b"":
                raise OSError("MQTT切断")
            self._set_timeout()
            return self._wait_msg(res)
        except Exception as e:
            print("MQTT確認エラー:", repr(e))
            self.close()
            raise
        finally:
            self._deadline = None


