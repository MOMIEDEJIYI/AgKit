import json
import re
from controller import create_file

def clean_json(text: str) -> str:
    # 去掉开头和结尾的 Markdown 代码块标记 ```json ... ```
    pattern = r"```(?:json)?\s*(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

def execute_actions(json_text: str):
    try:
        cleaned = clean_json(json_text)
        actions = json.loads(cleaned)
        for action in actions:
            act = action.get("action")
            params = action.get("params", {})

            if act == "create_file":
                create_file(params.get("file_name", "newfile.txt"), params.get("content", ""))
            else:
                print(f"[未知动作] {act}")
    except Exception as e:
        print("[解析错误]", e)
        print(json_text)
