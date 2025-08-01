import re
import os
import sys

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        # 返回项目根目录路径
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)

def extract_json_from_text(text: str) -> str:
    # 匹配 ```json ... ``` 或 ``` ... ``` 代码块内容
    pattern = r"```json(.*?)```|```(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    for match in matches:
        json_text = match[0] or match[1]
        if json_text:
            return json_text.strip()
    return text.strip()

def process_assistant_content(raw_content: str) -> str:
    import json, re
    try:
        # 尝试抽取 ```json ... ``` 中的 JSON
        m = re.search(r"```json\s*(\{.*?\})\s*```", raw_content, re.DOTALL)
        json_str = m.group(1) if m else raw_content

        data = json.loads(json_str)
        explanation = data.get("explanation", "")
        result = ""
        if "jsonrpc" in data:
            res_obj = data["jsonrpc"].get("result")
            if res_obj:
                # 根据情况格式化 result，比如转为字符串或列表文本
                if isinstance(res_obj, dict):
                    if "content" in res_obj:
                        content_val = res_obj["content"]
                        if isinstance(content_val, list):
                            result = "\n文件列表：\n" + "\n".join(content_val)
                        else:
                            result = str(content_val)
                    else:
                        result = str(res_obj)
                else:
                    result = str(res_obj)
        
        # 如果 explanation 和 result 有重复，避免重复显示
        if result and result.strip() not in explanation:
            return f"{explanation}\n{result}"
        else:
            return explanation or raw_content
    except Exception:
        # 解析失败，返回原文
        return raw_content

def get_abs_path_from_config_path(config_path: str, base_dir: str = None) -> str:
    if not config_path:
        return ""
    if os.path.isabs(config_path):
        return config_path
    if base_dir is None:
        base_dir = os.getcwd()  # 或你项目的根目录
    return os.path.abspath(os.path.join(base_dir, config_path))