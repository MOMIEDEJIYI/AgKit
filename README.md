#  Agent

支持插件机制的智能代理，可通过 CLI 或 GUI 方式运行。

---

## 快速开始

### 1. 准备环境

确保安装 Python 3.10+，然后执行（推荐使用conda管理python版本）：

```bash
pip install -r requirements.txt
```

并在根目录添加 `.env` 文件，配置模型 API KEY

```bash
PROVIDER=deepseek
DEEPSEEK_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

### 2. 启动方式

- 启动命令行版本（CLI 模式）：

```
python main_cli.py
```

- 启动图形界面版本（GUI 模式）：

```
python main_gui.py
```



### 3.项目结构

```bash
agent/            # 核心代理模块：对话管理、RPC 调用等
│
├─models/         # 模型客户端封装（Gemini，OpenAI系列直接使用包即可）
├─api/            # FastAPI 路由（聊天 / 会话接口）
├─common/         # 公共模块（错误码等）
├─model/          # 数据模型（Pydantic Schema）
├─plugins/        # 插件模块（执行命令 / 报表生成 / 文件操作）
│  ├─exec/
│  ├─network/
│  ├─report/
│  └─system/
├─ui/             # 图形界面（PyQt）
│  ├─assets/      # 样式资源
│  └─components/  # 组件封装
├─utils/          # 工具函数
├─main_cli.py     # CLI 启动入口
├─main_gui.py     # GUI 启动入口
├─rpc_registry.py # 工具方法注册器
├─config.py       # 配置加载
├─setup.py        # 打包配置
├─requirements.txt# 依赖列表
└─.env            # 环境变量（不提交到 Git）
```



### 4.Cli数据

#### 4.1未标注工具结果包装（tool_result_wrap=false）

请求示例：

```json
{
    "user_id": "user1", // 当前会话保存的文件夹
    "session_id": "", // 当前会话保存文件夹的会话文件，为空时新建
    "stream": true, // 是否使用流式输出（当前结果不明显，可以忽略）
    "message": "请帮我生成一篇完整的关于橡树的作文内容，文本长度不少于200字" // 对话
}
```



响应示例：

```json
{
    "success": true, // 顶层请求是否成功，通常表示请求流程是否出错（如参数校验、内部异常等）
    "reply": {
        "explanation": "", // 解释信息，可选字段，可用于 CLI 模式下提供额外说明，比如为什么失败
        "jsonrpc": {
            "jsonrpc": "2.0", // 表示使用的 JSON-RPC 协议版本，固定为 2.0
            "id": 1, // 请求对应的 ID，用于客户端请求与响应匹配
            "result": {
                "content": "✅ 已创建文件：橡树作文.txt", // 返回给用户的主要内容
                "done": true, // 是否已完成所有相关任务（比如写入文件），用于判断是否还需后续处理
                "success": true, // 当前操作（如创建文件）是否成功，细粒度成功标志
                "code": 0 // 操作结果码，0 表示成功，其他值可以定义对应的错误码
            }
        }
    },
    "session_id": "session_20250725_123252.json", // 本次会话标识
    "error": null // 错误信息对象，顶层错误时填充（如网络异常），无错误时为 null
}
```

### 

#### 4.2标注工具结果包装（tool_result_wrap=true）

请求示例：

```json
{
    "user_id": "user1",
    "session_id": "",
    "stream": true,
    "message": "帮我导出报表"
}
```

响应示例：

```json
{
    "success": true,
    "reply": {
        "text": {
            "explanation": "报表导出成功",   // 对任务执行的解释或提示说明
            "jsonrpc": {
                "jsonrpc": "2.0",          // JSON-RPC 协议版本
                "result": {
                    "content": "报表已成功导出为JSON格式文件", 
                                             // 给用户的文本回应
                    "done": true           // 是否完成任务
                },
                "id": 1
            }
        },
        "tool_result": {                   // 工具函数返回结果包装（适合 自定义携带参数给调用方使用）
            "content": {
                "type": "ui_command",      
                "command": "exportJsonFile"
            },
            "done": true,
            "success": true,
            "code": 0
        }
    },
    "session_id": "session_20250725_124144.json", // 会话标识
    "error": null
}
```



#### 4.3错误结果示例

请求示例：

```json
{
    "user_id": "user1",
    "session_id": "1234",
    "stream": true,
    "message": "请帮我生成一篇完整的关于橡树的作文内容，文本长度不少于200字"
}
```

响应示例：

```json
{
    "success": false,
    "reply": null,
    "session_id": null,
    "error": "[Errno 2] No such file or directory: 'conversation/history/user1\\\\1234'"
}
```



### 5.新增插件包

添加插件：

1.在 `plugins` 包下新增插件文件夹，作为独立模块使用；

2.在插件文件夹中添加 `__init__.py` 文件，以确保 Python 识别该目录为模块；

3.编写功能实现的 `.py` 文件，并使用装饰器 `@register_method` 对外暴露插件方法；

4.插件加载成功后，可在 `runtime` 中的方法快照中确认方法是否注册成功。



插件方法注册使用的 `@register_method` 装饰器支持以下字段配置

| 字段名           | 描述                                                         |
| ---------------- | ------------------------------------------------------------ |
| name             | 方法名称（必填）                                             |
| param_desc       | 方法参数描述（必填，若无参数请设置为 `param=None`）          |
| description      | 方法用途描述（必填，便于大模型理解功能意图）                 |
| needs_nlg        | 是否为二次对话（默认为 `false`，即 RPC 调用后不返回模型响应） |
| tool_result_wrap | 是否携带 RPC 调用结果返回（默认为 `false`）                  |



### 6.当前插件包

| 插件包  | 描述         | 是否验证 | 说明                                                         |
| ------- | ------------ | -------- | ------------------------------------------------------------ |
| exec    | 命令运行     | 否       | 支持执行本地命令（如 pip 安装）。尚未进行全面测试，需注意安全控制。 |
| network | 网络请求     | 否       | 用于发起 HTTP/HTTPS 请求。暂未测试代理、超时处理等边界情况。 |
| report  | 报表示例     | 是       | 插件示例，用于生成调用方结果示例。功能已通过基本验证。       |
| system  | 系统文件操作 | 是       | 支持读写、创建、删除本地文件。基本功能已验证，建议在受控目录下使用。 |



### 7.注意

- 某些插件（如 `exec` 和 `system`）具有一定风险，使用时请确保不会造成影响
- `exec` 和 `network` 插件目前尚未完全验证，使用时可能存在异常行为或错误处理不完整的问题
- `exec` 插件需依赖系统已有命令，如 `pip`、`ls` 等，执行失败可能与环境路径或权限有关
- `network` 插件未验证，等待验证后使用
- 所有插件支持扩展，若执行行为出现偏差，请确认是否为提示词（prompt）不完整或参数缺失所致（也不排除流程问题哈）



### 8.后续

- [ ] 请求时支持多模型切换（如 OpenAI / DeepSeek / 自建模型）
- [ ] 增加插件包完整性验证机制，防止加载不完整或异常插件
- [ ] 补充测试覆盖未验证插件（如 `exec` / `network`）
