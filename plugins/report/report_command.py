import os
from rpc_registry import register_method

@register_method(
  name="report.export_json",
  param_desc={},
  direct_response=True
)
def send_ui_command(params=None) -> dict:
  return {
      "type": "ui_command",
      "command": "export_json",
  }
