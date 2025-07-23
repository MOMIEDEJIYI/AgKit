# common/error_codes.py

class ErrorCode:
    # 通用错误
    UNKNOWN_ERROR = {
        "code": -32000,
        "message": "系统内部错误或插件未定义错误码"
    }

    # 参数错误
    MISSING_PARAM = {
        "code": -32001,
        "message": "缺失必要参数"
    }

    
    INVALID_PARAM = {
        "code": -32002,
        "message": "参数格式错误或不合法"
    }

    UNAUTHORIZED = {
        "code": -32003,
        "message": "未授权访问"
    }

    FORBIDDEN = {
        "code": -32004,
        "message": "禁止访问该资源"
    }

    NOT_FOUND = {
        "code": -32005,
        "message": "资源不存在"
    }

    TIMEOUT = {
        "code": -32006,
        "message": "请求超时"
    }

    UNKNOWN_METHOD = {
        "code": -32601,
        "message": "未知方法"
    }
