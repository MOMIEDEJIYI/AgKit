import os
from rpc_registry import register_method

@register_method(
  name="report.create_sales_report",
  param_desc={},
  needs_nlg=True, # 二次自然语言包装
  tool_result_wrap = True # 工具结果包装
)
def send_ui_command_create_sales_report(params=None) -> dict:
  return {
      "type": "ui_command",
      "command": "createNewReport",
      "params": {
        "reportType": "sales"
      },
  }

@register_method(
  name="report.create_inventory_report",
  param_desc={},
  needs_nlg=True, # 二次自然语言包装
  tool_result_wrap = True # 工具结果包装
)
def send_ui_command_create_inventory_report(params=None) -> dict:
  return {
      "type": "ui_command",
      "command": "createNewReport",
      "params": {
        "reportType": "inventory"
      },
  }

@register_method(
  name="report.create_customer_report",
  param_desc={},
  needs_nlg=True, # 二次自然语言包装
  tool_result_wrap = True # 工具结果包装
)
def send_ui_command_create_inventory_report(params=None) -> dict:
  return {
      "type": "ui_command",
      "command": "createNewReport",
      "params": {
        "reportType": "customer"
      },
  }


@register_method(
  name="report.create_sales_and_profits_report",
  param_desc={},
  needs_nlg=True, # 二次自然语言包装
  tool_result_wrap = True # 工具结果包装
)
def send_ui_command_create_inventory_report(params=None) -> dict:
  return {
      "type": "ui_command",
      "command": "createNewReport",
      "params": {
        "reportType": "multiMetrics"
      },
  }

@register_method(
  name="report.create_operational_statistics_report",
  param_desc={},
  needs_nlg=True, # 二次自然语言包装
  tool_result_wrap = True # 工具结果包装
)
def send_ui_command_create_inventory_report(params=None) -> dict:
  return {
      "type": "ui_command",
      "command": "createNewReport",
      "params": {
        "reportType": "summary"
      },
  }