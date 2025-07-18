# agent

下载运行https://github.com/MOMIEDEJIYI/report-dashboard
可以测试本项目的report插件

运行：

1.新建.env文件

2.在文件中添加DEEPSEEK_API_KEY="你的deepseek密钥"

3.1使用python main_cli.py运行服务

3.2使用python main_gui.py运行界面



添加插件：
1.在plugins包中新建文件夹

2.在文件夹中新建__init__.py表明为模块

3.新建py文件，在函数上加@register_method进行工具方法注册

4.运行后在runtime中的方法快照中查看方法是否注册



@register_method有以下字段

| 字段名           | 描述                                                    |
| ---------------- | ------------------------------------------------------- |
| name             | 方法名称，必须要有                                      |
| param_desc       | 方法参数，必须要有，不用参数也要给param=None            |
| needs_nlg        | 是否二次对话，默认false，rpc调用后不会返回模型          |
| tool_result_wrap | 是否携带rpc结果返回，默认false，rpc调用后不携带调用结果 |

