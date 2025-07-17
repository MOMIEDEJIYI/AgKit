import os
from rpc_registry import register_method

@register_method(
  name="report.export_json",
  param_desc={},
  # needs_nlg=True, # 二次自然语言包装
  tool_result_wrap = True # 工具结果包装
)
def send_ui_command_export(params=None) -> dict:
  return {
      "type": "ui_command",
      "command": "exportJsonFile",
  }
