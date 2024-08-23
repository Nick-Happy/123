from flask import Flask, request, jsonify
import requests
import json
import uuid
app = Flask(__name__)

url_v1 = "http://192.168.1.111:5670/api/v2/chat/completions"

@app.route('/chat', methods=['POST'])
def chat():
    client_payload = request.get_json()  # 从请求体中获得JSON数据
    print('入参',client_payload)
    # 检查请求体中的参数
    if "adam_id" in client_payload and "message" in client_payload:
        return database_chat(client_payload)
    elif "message" in client_payload:
        return knowledge_chat(client_payload)
    else:
        return jsonify({
            "status": "error",
            "message": "Invalid parameters"
        }), 400

def database_chat(payload):
    try:
        adam_id = payload.get("adam_id")
        message = payload.get("message")
        new_message = f"根据adam_id是{adam_id}回答以下问题：{message}"
        conv_uid = str(uuid.uuid4())

        url = url_v1
        payload = {
            "model": "deepseek_proxyllm",
            "messages": new_message,
            "stream": False,
            "temperature": 0,
            "max_new_tokens": 0,
            "conv_uid": conv_uid,
            "span_id": "string",
            "chat_mode": "chat_data",
            "chat_param": "zzh",
            "user_name": "root",
            "sys_code": "string",
            "incremental": True,
            "enable_vis": True
        }
    
        response = requests.post(url, json=payload)
        response.raise_for_status()  # 如果响应错误状态则抛出异常
        data = response.json()
        content = data.get("choices", [])[0].get("message", {}).get("content", "")

        start = content.find("<chart-view content=\"") + len("<chart-view content=\"")
        end = content.rfind("\" />")
        json_content = content[start:end]

        #解析json_content
        parsed_content = json.loads(json_content)
        data_content = parsed_content.get("data", [])
        
        if data_content == []:
            return jsonify({
                "status": False,
                "message": "查不到指定内容！",
                "content":""
            }), 500
        else:
            return jsonify({
                "status": True,
                "message": '',
                "content": json_content  # 返回整个内容
            }), 200
    except requests.exceptions.RequestException as e:
        error_message = "查询失败！"  # 将报错信息转为字符串
        return jsonify({
            "status": False,
            "message": f"Request failed: {error_message}",  # 将报错信息加入message
        }), 500
    except Exception as e:
        # 捕获所有其他未明确处理的异常
        return jsonify({
            "status": False,
            "message": f"出现意外错误：{str(e)}",
            "content": ""
        }), 500



def knowledge_chat(payload):
    message = payload.get("message")

    url = url_v1
    payload = {
        "model": "deepseek_proxyllm",
        "messages": message,
        "stream": 'false',
        "temperature": 0,
        "max_new_tokens": 0,
        "conv_uid": "string",
        "span_id": "string",
        "chat_mode": "chat_knowledge",
        "chat_param": "ASA"
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # 如果响应错误状态则抛出异常
        data = response.json()
        content = data.get("choices", [])[0].get("message", {}).get("content", "")

        json_content = content

        return jsonify({
            "status": "success",
            "message": json_content,
        }), 200
    except requests.exceptions.RequestException as e:
        error_message = "查询错误！"  # 将报错信息转为字符串
        return jsonify({
            "status": False,
            "message": f"Request failed: {error_message}",  # 将报错信息加入message
        }), 500

if __name__ == '__main__':
    app.run(host='192.168.1.111', port=8080, debug=True)