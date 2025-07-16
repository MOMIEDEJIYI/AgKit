from PyQt5.QtCore import QThread, pyqtSignal

class WorkerThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    thinking = pyqtSignal(str)

    def __init__(self, user_input, agent_service):
        super().__init__()
        self.user_input = user_input
        self.agent_service = agent_service

    def run(self):
        print("WorkerThread running")
        try:
            self.thinking.emit("助手正在思考中，请稍候...")
            result = self.agent_service.ask(self.user_input)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


    def stop(self):
        self.cancelled = True
        self.service.stop()  # 如果你支持取消调用的话
