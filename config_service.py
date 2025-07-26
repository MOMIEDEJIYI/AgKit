import os
import json
import threading

class ConfigService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, config_path="config.json"):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._init(config_path)
        return cls._instance

    def _init(self, config_path):
        self.config_path = config_path
        self._config = {}
        self._load()

    def _load(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                try:
                    self._config = json.load(f)
                except Exception:
                    self._config = {}
        else:
            self._config = {}

    def save(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self._config, f, ensure_ascii=False, indent=2)

    def get(self, key, default=None):
        return self._config.get(key, default)

    def set(self, key, value, save_immediately=True):
        self._config[key] = value
        if save_immediately:
            self.save()

    def get_all(self):
        return dict(self._config)

    # 获取某个配置节
    def get_section(self, section: str, default=None):
        return self._config.get(section, default or {})

    # 设置某个配置节
    def set_section(self, section: str, value: dict, save_immediately=True):
        self._config[section] = value
        if save_immediately:
            self.save()

    # 获取特定模型的配置
    def get_model_config(self, model_name: str):
        return self._config["agent"].get(model_name, None)

    # 获取当前使用的模型配置
    def get_current_model(self):
        return self.get("current_model", "default")

    # 设置当前使用的模型
    def set_current_model(self, model_name: str, save_immediately=True):
        self.set("current_model", model_name, save_immediately)

    # 切换模型
    def switch_model(self, model_name: str):
        model_config = self.get_model_config(model_name)
        if model_config:
            self.set_current_model(model_name)
            self.save()
        else:
            raise ValueError(f"Model {model_name} does not exist.")
    
    # 设置特定模型的配置
    def set_model_config(self, model_name: str, model_config: dict, save_immediately=True):
        if model_name not in self._config["agent"]:
            self._config["agent"][model_name] = {}
        self._config["agent"][model_name] = model_config
        if save_immediately:
            self.save()

    # 删除模型配置
    def delete_model_config(self, model_name: str, save_immediately=True):
        if model_name in self._config["agent"]:
            del self._config["agent"][model_name]
            if save_immediately:
                self.save()