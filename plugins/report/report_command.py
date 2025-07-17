import os
from rpc_registry import register_method

@register_method(
  name="report.export_json",
  param_desc={"description": "给前端发送导出 JSON 文件的 UI 操作指令"},
  direct_response=True
)
def send_ui_command() -> dict:
  return {
      "type": "ui_command",
      "command": "export_json",
      "args": {}  # 可选参数，可为空
  }
