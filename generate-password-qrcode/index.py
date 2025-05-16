from flask import Flask, request, jsonify
import json
import handler

app = Flask(__name__)

@app.route('/', methods=['POST'])
def main():
    req_data = request.data.decode('utf-8')
    response, status_code = handler.handle(req_data)
    # handler.handle renvoie un tuple (json_str, status_code)
    return jsonify(json.loads(response)), status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
