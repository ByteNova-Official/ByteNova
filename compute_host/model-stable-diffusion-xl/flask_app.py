from flask import Flask, request
from model_invoke import invoke
import requests, base64, json

app = Flask(__name__)

@app.route('/invoke', methods=['POST'])
def generate():
    rj = request.json
    text = rj['input']
    result = invoke(text)
    
    if 's3_upload_fields' not in rj:
        return result
    s3_upload_fields = json.loads(base64.b64decode(rj['s3_upload_fields'].encode()).decode())
    response = requests.post(s3_upload_fields['url'], data=s3_upload_fields['fields'], files={'file': open('generated_image.png', 'rb')})
    # Check if the upload was successful
    if response.status_code >= 300:
        return f'Upload failed with status code {response.status_code}, response: {response.text}'
    else:
        return "https://cdn.clustro.ai/" + s3_upload_fields['fields']['key']

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
