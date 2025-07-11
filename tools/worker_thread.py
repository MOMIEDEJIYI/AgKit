from PyQt5.QtCore import QThread, pyqtSignal
from agent.agent import Agent

class WorkerThread(QThread):
    finished = pyqtSignal(str)  # 传递模型返回内容

    def __init__(self, history):
        super().__init__()
        self.history = history
        self.agent = Agent()

    def run(self):
        result = self.agent.ask(self.history)
        self.finished.emit(result)
