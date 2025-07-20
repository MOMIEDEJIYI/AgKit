
class ErrorCode:
    # 通用错误
    MISSING_PARAM = {"code": 1001, "message": "缺少必要参数"}
    FILE_CREATION_FAILED = {"code": 1002, "message": "文件创建失败"}
    UNKNOWN_ERROR = {"code": 1999, "message": "未知错误"}

    # 插件系统错误（建议 2xxx 段）
    PLUGIN_LOAD_FAILED = {"code": 2001, "message": "插件加载失败"}
    PLUGIN_EXECUTION_FAILED = {"code": 2002, "message": "插件执行失败"}
    PLUGIN_TIMEOUT = {"code": 2003, "message": "插件执行超时"}
