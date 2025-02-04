from flask import Flask, request
from model_invoke import invoke

app = Flask(__name__)

@app.route('/invoke', methods=['POST'])
def generate():
    text = request.json['input']
    result = invoke(text)
    return result

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
