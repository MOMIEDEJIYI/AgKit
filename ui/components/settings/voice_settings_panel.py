from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFormLayout,
    QHBoxLayout, QFrame, QMessageBox, QComboBox, QCheckBox
)
from PyQt5.QtCore import Qt
import os
from utils.event_bus import event_bus
from utils import utils
from config_service import ConfigService
from ui.components.base.popup_dialog import PopupDialog
from ui.components.base.path_picker import PathPicker


class VoiceSettingsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.config_service = ConfigService()

        self.stt_path_picker = PathPicker(mode="directory")  # 目录模式
        self.tts_engine_combo = QComboBox()
        self.tts_enabled_checkbox = QCheckBox("启用语音输出(TTS)")

        self.tts_engine_combo.addItems(["pyttsx3", "edge-tts"])

        self.setup_ui()
        self._load_stylesheet()
        self.load_voice_settings()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        card_container = QFrame()
        card_container.setObjectName("settingsCard")
        card_layout = QVBoxLayout(card_container)
        card_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel("语言设置")
        title_label.setObjectName("cardTitle")
        card_layout.addWidget(title_label)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setVerticalSpacing(10)
        form_layout.setHorizontalSpacing(15)

        # STT模型路径
        form_layout.addRow(QLabel("语音识别模型路径(STT):"), self.stt_path_picker)
        # TTS使能
        form_layout.addRow(self.tts_enabled_checkbox)
        # TTS引擎选择
        form_layout.addRow(QLabel("语音合成引擎(TTS):"), self.tts_engine_combo)

        card_layout.addLayout(form_layout)

        # 保存按钮
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignRight)
        self.save_button = QPushButton("保存设置")
        self.save_button.setFixedSize(150, 40)
        self.save_button.setObjectName("primaryButton")
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)

        card_layout.addLayout(button_layout)
        main_layout.addWidget(card_container)

    def load_voice_settings(self):
        voice_cfg = self.config_service.get_section("voice") or {}

        stt_cfg = voice_cfg.get("stt", {})
        tts_cfg = voice_cfg.get("tts", {})

        self.stt_path_picker.setText(stt_cfg.get("path", "models/vosk-model-small-cn-0.22"))
        self.tts_enabled_checkbox.setChecked(tts_cfg.get("enabled", False))
        engine = tts_cfg.get("engine", "pyttsx3")
        idx = self.tts_engine_combo.findText(engine)
        if idx >= 0:
            self.tts_engine_combo.setCurrentIndex(idx)

    def save_settings(self):
      try:
          stt_path = self.stt_path_picker.text().strip()
          if not stt_path:
              QMessageBox.warning(self, "警告", "语音识别模型路径不能为空")
              return

          tts_enabled = self.tts_enabled_checkbox.isChecked()
          tts_engine = self.tts_engine_combo.currentText()

          new_cfg = {
              "stt": {
                  "path": stt_path
              },
              "tts": {
                  "enabled": tts_enabled,
                  "engine": tts_engine
              }
          }

          self.config_service.set_section("voice", new_cfg)
          self.config_service.save()

          # 发布事件，通知其他模块更新语音配置
          event_bus.publish("voice_settings_changed")
          
          dlg = PopupDialog(title="成功", message="语音设置已保存！")
          dlg.exec_()

      except Exception as e:
          QMessageBox.critical(self, "保存失败", str(e))

    def _load_stylesheet(self):
        qss_path = utils.resource_path("assets/styles/settings/voice_settings_panel.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
