import os
from dotenv import load_dotenv

load_dotenv()  # 这行会加载 .env 文件的内容进 os.environ

API_KEY = os.getenv("DEEPSEEK_API_KEY")