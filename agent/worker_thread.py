from PyQt5.QtCore import QThread, pyqtSignal
import logging

logger = logging.getLogger(__name__)
class WorkerThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    thinking = pyqtSignal(str)

    def __init__(self, user_input, agent_service, stream_mode=False):
        super().__init__()
        self.user_input = user_input
        self.agent_service = agent_service
        self.stream_mode = stream_mode

    def run(self):
        try:
            def progress(msg):
                self.thinking.emit(msg)

            if self.stream_mode:
                result = self.agent_service.ask_stream(
                    self.user_input,
                    check_cancel=self.check_cancel,
                    progress_callback=progress
                )
            else:
                result = self.agent_service.ask(
                    self.user_input,
                    check_cancel=self.check_cancel,
                    progress_callback=progress
                )

            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

    def stop(self):
        logger.info("WorkerThread: 停止请求")
        self.agent_service.stop()

    def check_cancel(self):
        cancelled = self.agent_service.is_cancelled()
        return cancelled
