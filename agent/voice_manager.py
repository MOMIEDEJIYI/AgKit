import os
import platform
import subprocess
import tempfile
import asyncio
import queue
import sounddevice as sd
import json
import pyttsx3

class VoiceManager:
    def __init__(self, stt_config=None, tts_engine="pyttsx3", tts_enabled=True):
        self.tts_engine = tts_engine
        self.tts_enabled = tts_enabled

        # 初始化 TTS 引擎
        if tts_engine == "pyttsx3":
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
        elif tts_engine == "edge-tts":
            self.engine = None  # 异步，运行时调用
        else:
            print(f"未知 TTS 引擎: {tts_engine}")
            self.engine = None

        # 初始化 STT 引擎
        self.stt_engine = None
        self.stt_model = None
        self.stt_recognizer = None

        if stt_config is None:
            stt_config = {}

        self.stt_engine = stt_config.get("engine", "vosk")
        self.stt_model_path = stt_config.get("path", "")

        if self.stt_engine == "vosk":
            try:
                from vosk import Model, KaldiRecognizer
                if os.path.exists(self.stt_model_path):
                    self.stt_model = Model(self.stt_model_path)
                    self.stt_recognizer = KaldiRecognizer(self.stt_model, 16000)
                else:
                    print(f"Vosk 模型路径不存在: {self.stt_model_path}")
            except ImportError:
                print("未安装 vosk，无法使用该STT引擎")
        elif self.stt_engine == "whisper":
            # TODO: 你可以初始化 whisper 模型
            self.whisper_model = None
            print("Whisper STT 引擎暂未实现")
        else:
            print(f"未知 STT 引擎: {self.stt_engine}")

    def speak(self, text):
        if not self.tts_enabled:
            return
        if not text.strip():
            return

        if self.tts_engine == "pyttsx3":
            self.engine.say(text)
            self.engine.runAndWait()

        elif self.tts_engine == "edge-tts":
            asyncio.run(self._edge_tts_play(text))
        else:
            print(f"未知 TTS 引擎: {self.tts_engine}")

    async def _edge_tts_play(self, text):
        import edge_tts

        communicate = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            temp_file = f.name
            await communicate.save(temp_file)

        try:
            if platform.system() == "Windows":
                subprocess.run([
                    "powershell", "-c",
                    f"(New-Object Media.SoundPlayer '{temp_file}').PlaySync();"
                ])
            else:
                player = "afplay" if platform.system() == "Darwin" else "mpg123"
                subprocess.run([player, temp_file])
        finally:
            os.remove(temp_file)

    def listen(self, duration=5):
        if self.stt_engine == "vosk":
            return self._listen_vosk(duration)
        elif self.stt_engine == "whisper":
            return self._listen_whisper(duration)
        else:
            print(f"未知 STT 引擎: {self.stt_engine}")
            return ""

    def _listen_vosk(self, duration):
        if not self.stt_recognizer:
            print("Vosk 识别器未初始化")
            return ""

        q = queue.Queue()

        def callback(indata, frames, time, status):
            if status:
                print(status)
            q.put(bytes(indata))

        try:
            with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                                channels=1, callback=callback):
                print("开始录音，请讲话...")
                for _ in range(int(16000 / 8000 * duration * 2)):  # duration秒
                    data = q.get()
                    if self.stt_recognizer.AcceptWaveform(data):
                        break

                result = json.loads(self.stt_recognizer.FinalResult())
                text = result.get("text", "")
                print("识别结果:", text)
                return text
        except Exception as e:
            print(f"录音失败: {e}")
            return ""

    def _listen_whisper(self, duration):
        # 这里放你调用whisper的录音和识别流程
        print("Whisper 识别暂未实现")
        return ""
