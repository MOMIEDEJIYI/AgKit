import subprocess
from agent.rpc_registry import register_method
from agent.models.rpc_base import RpcResultBase
from plugins.system.error_codes import ErrorCode

# 允许执行的命令白名单（只允许pip相关命令作为示例）
ALLOWED_COMMANDS = [
    "pip install",
    "pip uninstall",
    "pip list"
]

@register_method(
    name="exec.execute_command", param_desc={"command": "要执行的命令"},
    description="执行命令",
)
def execute_command(command: str) -> str:
    # 简单检查命令是否以允许前缀开头，防止执行任意命令
    if not any(command.strip().startswith(allowed) for allowed in ALLOWED_COMMANDS):
        return RpcResultBase("❌ 命令不被允许执行", success=False, code=ErrorCode.FILE_READ_ERROR["code"]).to_dict()

    try:
        # 执行命令，捕获输出
        result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding='utf-8',
            timeout=60  # 超时保护
        )
        return result.stdout.strip()
    except Exception as e:
        return RpcResultBase(f"❌ 命令执行失败: {e}", success=False, code=ErrorCode.FILE_READ_ERROR["code"]).to_dict()
