from PyQt5.QtCore import QThread, pyqtSignal
from agent import ask_agent
class WorkerThread(QThread):
    finished = pyqtSignal(str)  # 传递模型返回内容

    def __init__(self, history):
        super().__init__()
        self.history = history

    def run(self):
        # 在这里调用耗时操作
        result = ask_agent(self.history)
        self.finished.emit(result)
