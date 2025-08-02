# agent/cluster/node_server.py
import json
from flask import Flask, request, jsonify
from agent.rpc_handler import handle_rpc_request

def create_node_server(agent_service, host="0.0.0.0", port=5001):
    from flask import Flask, request, jsonify
    app = Flask(__name__)

    @app.route("/rpc", methods=["POST"])
    def rpc():
        data = request.json
        if not data:
            return jsonify({"error": "invalid request"}), 400
        # 直接调用函数处理请求
        result = handle_rpc_request(json.dumps(data))
        return jsonify(result)

    app.run(host=host, port=port)
