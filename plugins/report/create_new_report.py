import os
from rpc_registry import register_method
from agent.models.rpc_base import RpcResultBase

@register_method(
  name="report.create_sales_report",
  param_desc={},
  needs_nlg=True, # 二次自然语言包装
  tool_result_wrap = True # 工具结果包装
)
def send_ui_command_create_sales_report(params=None) -> dict:
  return RpcResultBase({
      "type": "ui_command",
      "command": "createNewReport",
      "params": {
        "id": "sales",
        "name": "销售报表"
      },
  }).to_dict()

@register_method(
  name="report.create_inventory_report",
  param_desc={},
  needs_nlg=True, # 二次自然语言包装
  tool_result_wrap = True # 工具结果包装
)
def send_ui_command_create_inventory_report(params=None) -> dict:
  return RpcResultBase({
      "type": "ui_command",
      "command": "createNewReport",
      "params": {
        "id": "inventory",
        "name": "库存报表"
      },
  }).to_dict()

@register_method(
  name="report.create_customer_report",
  param_desc={},
  needs_nlg=True, # 二次自然语言包装
  tool_result_wrap = True # 工具结果包装
)
def send_ui_command_create_customer_report(params=None) -> dict:
  return RpcResultBase({
      "type": "ui_command",
      "command": "createNewReport",
      "params": {
        "id": "customer",
        "name": "客户报表"
      },
  }).to_dict()


@register_method(
  name="report.create_sales_and_profits_report",
  param_desc={},
  needs_nlg=True, # 二次自然语言包装
  tool_result_wrap = True # 工具结果包装
)
def send_ui_command_create_sales_and_profits_report(params=None) -> dict:
  return RpcResultBase({
      "type": "ui_command",
      "command": "createNewReport",
      "params": {
        "id": "multiMetrics",
        "name": "销售与利润趋势"
      },
  }).to_dict()

@register_method(
  name="report.create_operational_statistics_report",
  param_desc={},
  needs_nlg=True, # 二次自然语言包装
  tool_result_wrap = True # 工具结果包装
)
def send_ui_command_create_operational_statistics_report(params=None) -> dict:
  return RpcResultBase({
      "type": "ui_command",
      "command": "createNewReport",
      "params": {
        "id": "summary",
        "name": "运营统计"
      },
  }).to_dict()