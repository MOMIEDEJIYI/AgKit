# rpc_base.py

class RpcBase:
    jsonrpc: str = "2.0"

class RpcResponse(RpcBase):
    def __init__(self, result=None, error=None, id=None):
        self.result = result
        self.error = error
        self.id = id

    def to_dict(self):
        base = {
            "jsonrpc": self.jsonrpc,
            "id": self.id
        }
        if self.error:
            base["error"] = self.error
        else:
            base["result"] = self.result
        return base

class RpcRequest(RpcBase):
    def __init__(self, method: str, params: dict, id: str):
        self.method = method
        self.params = params
        self.id = id

class RpcNotification(RpcBase):
    def __init__(self, method: str, params: dict):
        self.method = method
        self.params = params
