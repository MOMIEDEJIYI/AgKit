class ErrorCode:
    # ==== 通用错误段：1000-1099 ====
    MISSING_PARAM = {"code": 1001, "message": "缺少必要参数"}
    UNKNOWN_ERROR = {"code": 1002, "message": "未知错误"}

    # ==== 文件操作错误段：1100-1199 ====
    FILE_NAME_MISSING = {"code": 1101, "message": "缺少文件名"}
    FILE_CREATION_FAILED = {"code": 1102, "message": "文件创建失败"}
    FILE_WRITE_ERROR = {"code": 1103, "message": "文件写入失败"}
    FILE_READ_ERROR = {"code": 1104, "message": "文件读取失败"}
    FOLDER_NOT_FOUND = {"code": 1105, "message": "路径不存在或不是文件夹"}
    FILE_DEPENDENCY_ANALYSIS_ERROR = {"code": 1106, "message": "文件依赖分析失败"}

    # 可选扩展
    FILE_DELETE_FAILED = {"code": 1107, "message": "文件删除失败"}
    FOLDER_READ_ERROR = {"code": 1108, "message": "文件夹读取失败"}
    INVALID_FILE_PATH = {"code": 1109, "message": "非法的文件路径"}
    FILE_ALREADY_EXISTS = {"code": 1110, "message": "文件已存在"}
    UNSUPPORTED_FILE_EXTENSION = {"code": 1111, "message": "不支持的文件扩展名"}

    # ==== 插件系统错误段：2000-2099 ====
    PLUGIN_LOAD_FAILED = {"code": 2001, "message": "插件加载失败"}
    PLUGIN_EXECUTION_FAILED = {"code": 2002, "message": "插件执行失败"}
    PLUGIN_TIMEOUT = {"code": 2003, "message": "插件执行超时"}
