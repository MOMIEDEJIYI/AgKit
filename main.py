from agent import ask_agent
from rpc_handler import handle_rpc_request
from controller import ChatContext
from dotenv import load_dotenv
load_dotenv()

SYSTEM_PROMPT = "你是遵守 JSON-RPC 2.0 协议的智能助手，返回符合规范的 JSON-RPC 请求。"

def main():
    context = ChatContext(SYSTEM_PROMPT)
    print("输入 '退出' 结束")

    request_id = 1

    while True:
        user_input = input("你：")
        if user_input.lower() in ["退出", "exit", "quit"]:
            break

        context.add_user_message(user_input)
        history = context.get_history()

        response = ask_agent(history)
        context.add_assistant_message(response)

        print("\n[模型 JSON-RPC 请求]:")
        print(response)

        rpc_response = handle_rpc_request(response)
        print("\n[执行结果]:")
        print(rpc_response)

        # 读取文件后，把文件内容也加到上下文，方便后续对话
        if "result" in rpc_response and "read_file" in response:
            file_content = rpc_response["result"]
            context.add_assistant_message(f"文件内容:\n{file_content}")

        request_id += 1

if __name__ == "__main__":
    main()
