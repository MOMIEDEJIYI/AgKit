# cluster_proxy.py (集群伪装插件)
from agent.rpc_registry import register_method
from plugins.cluster.cluster_manager import ClusterManager
from agent.models.rpc_base import RpcResultBase
from plugins.system.error_codes import ErrorCode
from plugins.cluster.config_service import ClusterConfigService  # 插件自己的配置

cluster_manager = ClusterManager()
cluster_config = ClusterConfigService()

def _get_cluster_description():
    """动态生成方法描述，把节点信息写进去"""
    nodes = cluster_config.get("nodes", {})
    if not nodes:
        return "将请求转发到指定的集群节点。目前没有配置任何节点。"
    
    desc = "将请求转发到指定的集群节点。参数需包含 'node' 字段，"
    desc += "可选携带 'intent' 字段描述调用意图。"
    desc += "\n\n可用节点："
    for name, info in nodes.items():
        if not info.get("enabled", True):
            continue
        desc += f"\n- {name}: {info.get('description', '')} ({info.get('url', '未知地址')})"
    return desc


@register_method(
    name="cluster.forward",
    description=_get_cluster_description(),
    param_desc={
        "node": "string, 必填，目标节点的名称，例如 'report' 或 'exec'",
        "intent": "string, 选填，自然语言描述调用意图，方便接收节点理解",
    }
)
def cluster_forward(params=None):
    if not params:
        return RpcResultBase("缺少参数，无法转发", success=False, code=ErrorCode.FILE_READ_ERROR["code"]).to_dict()
    node = params.get("node")
    if not node:
        return RpcResultBase("缺少 node 参数，无法转发", success=False, code=ErrorCode.FILE_READ_ERROR["code"]).to_dict()
    intent = params.get("intent", "")
    method = params.get("method")
    return cluster_manager.forward(node=node, method=method, intent=intent)
