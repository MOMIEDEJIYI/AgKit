import os
from dotenv import load_dotenv

load_dotenv(override=True)

print("当前工作目录：", os.getcwd())

PROVIDER = os.getenv("PROVIDER", "deepseek").lower()

if PROVIDER == "deepseek":
    API_KEY = os.getenv("DEEPSEEK_API_KEY")
    BASE_URL = "https://api.deepseek.com/v1"
    MODEL = "deepseek-chat"
elif PROVIDER == "gemini":
    API_KEY = os.getenv("GEMINI_API_KEY")
    MODEL = "gemini-2.0-flash"
    BASE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
elif PROVIDER == "openai":
    API_KEY = os.getenv("OPENAI_API_KEY")
    BASE_URL = "https://api.openai.com/v1"
    MODEL = "gpt-3.5-turbo"
else:
    raise ValueError(f"Unsupported LLM provider: {PROVIDER}, supported providers: deepseek, gemini, openai")

print(f"PROVIDER: {PROVIDER}")
print(f"BASE_URL: {BASE_URL}")
print(f"MODEL: {MODEL}")