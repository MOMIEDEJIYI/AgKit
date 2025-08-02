# agent/cluster/node_client.py
import requests
from utils import utils


class NodeClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def call(self, method: str, params: dict) -> dict:
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": utils.generate_uuid()
        }

        resp = requests.post(f"{self.base_url}/rpc", json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
