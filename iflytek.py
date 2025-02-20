import hashlib
import hmac
import base64
import pyaudio
import json
import threading
import wave
from datetime import datetime
from time import mktime
from urllib.parse import urlparse, urlencode
from wsgiref.handlers import format_date_time
import websocket

APP_ID = "c3f28266"
API_KEY = "77e4a1df6809b95dde567758d7011a23"
API_SECRET = "MTJlZTg2NDc0ODJlY2ExZDdlMjdlZDcy"
AUDIO_FILE_PATH = "record.wav"

def generate_auth_url():
    #生成带鉴权参数的WebSocket连接URL
    base_url = "wss://iat-api.xfyun.cn/v2/iat"
    host = urlparse(base_url).netloc
    date = format_date_time(mktime(datetime.now().timetuple()))
    
    # 生成签名
    signature_origin = f"host: {host}\ndate: {date}\nGET /v2/iat HTTP/1.1"
    signature_sha = hmac.new(
        API_SECRET.encode("utf-8"),
        signature_origin.encode("utf-8"),
        hashlib.sha256
    ).digest()
    signature = base64.b64encode(signature_sha).decode()
    
    # 构造鉴权头
    authorization = (
        f'api_key="{API_KEY}", algorithm="hmac-sha256", '
        f'headers="host date request-line", signature="{signature}"'
    )
    authorization_b64 = base64.b64encode(authorization.encode()).decode()
    
    # 构造查询参数
    params = {
        "host": host,
        "date": date,
        "authorization": authorization_b64
    }
    return f"{base_url}?{urlencode(params)}"

class WavProcessor:    
    @staticmethod
    def validate(file_path):
        """验证WAV文件格式"""
        try:
            with wave.open(file_path, 'rb') as f:
                params = f.getparams()
                if params.nchannels != 1:
                    return False, "必须为单声道音频"
                if params.framerate != 16000:
                    return False, "采样率必须为16000Hz"
                if params.sampwidth != 2:
                    return False, "必须为16位位深度"
                if params.comptype != 'NONE':
                    return False, "必须使用PCM编码"
                return True, "验证通过"
        except Exception as e:
            return False, f"文件错误：{str(e)}"

    @staticmethod
    def read_pcm(file_path):
        """读取PCM数据"""
        with wave.open(file_path, 'rb') as f:
            return f.readframes(f.getnframes())

class SpeechRecognizer:    
    def __init__(self):
        self.ws = None
        self.is_running = True
        self.final_text = ""

    def on_open(self, ws):
        """连接建立回调"""
        print("连接成功，开始传输数据...")
        
        def send_data():
            try:
                # 验证并读取音频
                valid, msg = WavProcessor.validate(AUDIO_FILE_PATH)
                if not valid:
                    raise ValueError(msg)
                
                pcm_data = WavProcessor.read_pcm(AUDIO_FILE_PATH)
                print(f"音频数据加载完成，总长度：{len(pcm_data)}字节")

                # 发送初始化帧
                init_frame = {
                    "common": {"app_id": APP_ID},
                    "business": {
                        "language": "zh_cn",
                        "domain": "iat",
                        "accent": "mandarin",
                        "dwa": "wpgs",
                        "ptt":0
                    },
                    "data": {
                        "status": 0,
                        "format": "audio/L16;rate=16000",
                        "encoding": "raw"
                    }
                }
                ws.send(json.dumps(init_frame))

                # 分块发送音频
                chunk_size = 1280
                for i in range(0, len(pcm_data), chunk_size):
                    if not self.is_running:
                        break
                    chunk = pcm_data[i:i+chunk_size]
                    ws.send(json.dumps({
                        "data": {
                            "status": 1,
                            "audio": base64.b64encode(chunk).decode()
                        }
                    }))

                # 发送结束帧
                ws.send(json.dumps({"data": {"status": 2}}))
                print("音频传输完成")

            except Exception as e:
                print(f"数据传输失败：{str(e)}")
                self.is_running = False
                ws.close()

        threading.Thread(target=send_data).start()

    def on_message(self, ws, message):
        """消息处理回调"""
        try:
            resp = json.loads(message)
            if resp["code"] != 0:
                print(f"错误代码 {resp['code']}: {resp['message']}")
                return

            data = resp.get("data", {})
            if not data:
                return

            if "result" in data:
                result = data["result"]
                text = "".join(w["cw"][0]["w"] for w in result["ws"])
                
                # 动态修正处理
                if result.get("pgs") == "rpl":
                    self.latest_revised = text
                    print(f"修正结果：{text}")
                else:
                    print(f"识别中：{text}")
                
                # 最终结果
                if result["ls"]:
                    final = self.latest_revised if self.latest_revised else text
                    self.final_text = final.rstrip("。，！？；")
                    print(f"最终结果：{self.final_text}")
                    self.is_running = False

        except Exception as e:
            print(f"消息解析失败：{str(e)}")

    def on_error(self, ws, error):
        """错误回调"""
        print(f"发生错误：{str(error)}")
        self.is_running = False

    def on_close(self, ws, status, msg):
        """关闭回调"""
        print(f"连接关闭 [{status}]: {msg}")
        self.is_running = False

    def start(self):
        """启动识别"""
        # 预验证音频文件
        valid, msg = WavProcessor.validate(AUDIO_FILE_PATH)
        if not valid:
            print(f"启动失败：{msg}")
            return

        # 建立连接
        self.ws = websocket.WebSocketApp(
            generate_auth_url(),
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        print("启动识别服务...")
        self.ws.run_forever()

def record_audio(output_filename, record_seconds):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000

    audio = pyaudio.PyAudio()

    try:
        stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    except Exception as e:
        print(f"无法访问麦克风: {str(e)}")
        return

    print(f"开始录音 {record_seconds} 秒...")
    frames = []

    for _ in range(0, int(RATE / CHUNK * record_seconds)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("录音结束，保存文件...")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    wf = wave.open(output_filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    print(f"音频文件已保存到 {output_filename}")


def main():
    input("按回车开始录音...")
    record_audio(AUDIO_FILE_PATH, 5)
    recognizer = SpeechRecognizer()
    recognizer.start()
    return recognizer.final_text

if __name__ == "__main__":
    main()