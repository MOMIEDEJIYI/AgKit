import re
import json
def extract_json_from_text(text: str) -> str:
    # 匹配 ```json ... ``` 或 ``` ... ``` 代码块内容
    pattern = r"```json(.*?)```|```(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    for match in matches:
        json_text = match[0] or match[1]
        if json_text:
            return json_text.strip()
    return text.strip()
