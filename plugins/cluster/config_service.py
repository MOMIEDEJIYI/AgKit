import os
import json
import threading

class ClusterConfigService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, config_path=None):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    # 默认放到插件目录下
                    if config_path is None:
                        base_dir = os.path.dirname(__file__)
                        config_path = os.path.join(base_dir, "config.json")
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

    # 获取节点配置
    def get_nodes(self):
        return self._config.get("nodes", {})

    def get_node(self, name: str):
        return self.get_nodes().get(name)

    def set_node(self, name: str, config: dict, save_immediately=True):
        nodes = self._config.setdefault("nodes", {})
        nodes[name] = config
        if save_immediately:
            self.save()
