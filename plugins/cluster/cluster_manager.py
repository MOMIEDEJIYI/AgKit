import requests
from utils import utils
from config_service import ConfigService
from agent.models.rpc_base import RpcResultBase
class ClusterManager:
    def __init__(self):
        self.config_service = ConfigService()
        self.nodes = {}  # 启用的节点字典
        self.reload_config()

    def reload_config(self):
        cluster_cfg = self.config_service.get_section("cluster", {})
        all_nodes = cluster_cfg.get("nodes", {})
        # 只保留启用的节点
        self.nodes = {name: info for name, info in all_nodes.items() if info.get("enabled", False)}

    def save_nodes(self):
        cluster_cfg = self.config_service.get_section("cluster", {})
        cluster_cfg["nodes"] = self.get_all_nodes()  # 可能需要实现get_all_nodes包含禁用节点
        self.config_service.set_section("cluster", cluster_cfg)

    def get_all_nodes(self) -> dict:
        """返回所有节点（包括禁用）"""
        cluster_cfg = self.config_service.get_section("cluster", {})
        return cluster_cfg.get("nodes", {})

    def add_or_update_node(self, node_name: str, node_info: dict, enabled=True):
        all_nodes = self.get_all_nodes()
        node_info["enabled"] = enabled
        all_nodes[node_name] = node_info
        cluster_cfg = self.config_service.get_section("cluster", {})
        cluster_cfg["nodes"] = all_nodes
        self.config_service.set_section("cluster", cluster_cfg)
        self.reload_config()

    def remove_node(self, node_name: str):
        all_nodes = self.get_all_nodes()
        if node_name in all_nodes:
            del all_nodes[node_name]
            cluster_cfg = self.config_service.get_section("cluster", {})
            cluster_cfg["nodes"] = all_nodes
            self.config_service.set_section("cluster", cluster_cfg)
            self.reload_config()


    def forward(self, node: str, method: str = None, params: dict = None, intent: str = "") -> dict:
        if node not in self.nodes:
            return RpcResultBase(f"节点 '{node}' 不存在或未启用", success=False, code=-1).to_dict()

        node_info = self.nodes[node]
        url = node_info.get("url")
        if not url:
            return RpcResultBase(f"节点 '{node}' 未配置有效 URL", success=False, code=-1).to_dict()

        payload = {
            "jsonrpc": "2.0",
            "method": method or "",
            "params": params or {},
            "id": 1,
            "intent": intent,
        }

        try:
            resp = requests.post(url, json=payload, timeout=10)
            resp.raise_for_status()
            resp_json = resp.json()
        except Exception as e:
            return RpcResultBase(f"请求节点 '{node}' 失败: {e}", success=False, code=-1).to_dict()

        # 处理节点返回的 JSON-RPC 响应
        if "error" in resp_json:
            msg = resp_json["error"].get("message", "远程节点执行失败")
            code = resp_json["error"].get("code", -32000)
            return RpcResultBase(msg, success=False, code=code).to_dict()
        elif "result" in resp_json:
            # result 字段通常是实际返回结果
            return RpcResultBase(str(resp_json["result"]), success=True).to_dict()

        # fallback
        return RpcResultBase("未知响应格式", success=False, code=-32000).to_dict()

