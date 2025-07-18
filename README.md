# agent

下载运行https://github.com/MOMIEDEJIYI/report-dashboard
可以测试本项目

新建.env文件，在文件中添加DEEPSEEK_API_KEY="你的deepseek密钥"

使用python main_cli.py运行服务

使用python main_gui.py运行界面

插件包为plugins，添加插件时新建自己的包，将方法贴上@register_method

@register_method有以下字段

| 字段名           | 描述                                                    |
| ---------------- | ------------------------------------------------------- |
| name             | 方法名称，必须要有                                      |
| param_desc       | 方法参数，必须要有，不用参数也要给param=None            |
| needs_nlg        | 是否二次对话，默认false，rpc调用后不会返回模型          |
| tool_result_wrap | 是否携带rpc结果返回，默认false，rpc调用后不携带调用结果 |