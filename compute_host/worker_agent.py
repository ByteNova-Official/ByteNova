import socketio
import argparse
import time
import requests
import json
import utils
import subprocess
import sys
import os

parser = argparse.ArgumentParser(description='Python Socket.IO Client for Workers')
parser.add_argument('--worker_id', type=str, default=os.environ.get("CLUSTROAI_WORKER_ID", None),
                    help='the ID of the worker')
parser.add_argument('--server_url', type=str, default='http://api.clustro.ai:5000',
                    help='backend server url')
parser.add_argument('--local_service_port', type=str, default='8000',
                    help='local server port')

args = parser.parse_args()

if args.worker_id is None:
    print("Error: --worker_id is required or CLUSTROAI_WORKER_ID should be set in environment variables.")
    sys.exit(1)

worker_id = args.worker_id
server_url = args.server_url
local_service_port = args.local_service_port

sio = socketio.Client()
local_inference_service_port = int(local_service_port)
local_inference_service_url_base = f'http://localhost:{local_inference_service_port}'
local_inference_service_url = local_inference_service_url_base + '/invoke'
local_inference_service_url_ping = local_inference_service_url_base + '/ping'

headers = {'Content-Type': 'application/json'}

@sio.event
def connect():  
    print(f'I am connected to the server! With namespace: {sio.namespaces}')

@sio.on('request_worker_id')
def on_request_worker_id(data):
    print(data['data'])  # prints "Please provide worker id."
    worker_sys_info = utils.get_system_info()
    while not sio.namespaces:
        print('Waiting for namespace in other thread to be ready...')
        time.sleep(0.1)
        
    sio.emit('provide_worker_id', {'id': worker_id, 'gpu_name': worker_sys_info['gpu_name'], 'gpu_memory_gb': worker_sys_info['gpu_memory_gb'], 'free_disk_gb': worker_sys_info['free_disk_gb'], 'ip': worker_sys_info['ip'] })

@sio.on('worker_session_established')
def on_worker_session_established(data):
    print(data)
    sio.emit('start')

@sio.on('message')
def on_message(data):
    print(data)

@sio.on('prepare_model')
def on_prepare_model(data):
    print(f"Preparing model... {data}")
    model_artifact = data['model_artifact']
    model_version = data['model_version']
    model_invoke_function = data['model_invoke_function']
    model_file_name = utils.get_model_repo(model_artifact, model_version, model_invoke_function)
    # Check if port is in use and kill the process
    print(f"Pulled repo URL {model_artifact}")
    try:
        result = subprocess.check_output(['lsof', '-i', f':{local_inference_service_port}', '-t'])
        pid = result.strip().decode('utf-8')
        if pid:
            print(f'Found exisitng process using port {local_inference_service_port}: {pid}. Killing it...')
            subprocess.run(['kill', '-9', pid])
    except subprocess.CalledProcessError:
        print(f'No process using port {local_inference_service_port}')
        pass  # No process using port
    print('Starting Flask app...')

    # Spawn the Flask app as a subprocess
    process = subprocess.Popen(['python3', 'flask_app.py', f'--port={local_inference_service_port}'], 
                           cwd=model_file_name, 
                           preexec_fn=os.setsid,
                           stderr=subprocess.PIPE)

    # Counter for elapsed time
    elapsed_time = 0
    deployment_timeout = 1800  # 30 minutes
    # Keep sending GET requests to /ping until a 200 OK response is received
    while True:
        # Fail if elapsed time is greater than deployment_timeout or subprocess.Popen exited with error
        if elapsed_time > deployment_timeout:
            print("Deployment timed out.")
            sio.emit('model_deployment_failed', {'model_artifact': model_artifact , 'total_time_spent': elapsed_time, 'error': 'timeout'})  
            break
        process_return_code = process.poll()
        if process_return_code is not None and process_return_code != 0:
            error_message = process.stderr.read().decode() if process.stderr else "Unknown error"
            sio.emit('model_deployment_failed', {'model_artifact': model_artifact , 'total_time_spent': elapsed_time, 'error': error_message}) 
            break 

        try:
            response = requests.get(local_inference_service_url_ping)
            if response.status_code == 200:
                break
        except:
            pass  # Handle connection refused error

        time.sleep(1)
        elapsed_time += 1
        
        # Check if elapsed time is a multiple of 60 to print a message every minute
        if elapsed_time % 60 == 0:
            print(f"Waiting for Flask app to start... {elapsed_time//60} minute(s) elapsed.")
    print('Flask app started successfully!')
    sio.emit('finish_model_deployment', {'model_artifact': model_artifact , 'total_time_spent': elapsed_time})

@sio.on('execute_invocation')
def on_execute_invocation(data):
    invocation_id = str(data['invocation_id'])
    input_string = data['input']
    print(data)
    print(f'working on invocation {invocation_id}...')
    invoke_data = {"input": input_string}
    if 's3_upload_fields' in data:
        invoke_data["s3_upload_fields"] = data["s3_upload_fields"]
    try:
        response = requests.post(local_inference_service_url, headers=headers, data=json.dumps(invoke_data), timeout=120)
        result, error = "", ""
        if response.status_code != 200:
            error = response.text
        else:
            result = response.text
        print(f"{invocation_id} result {result}")
        sio.emit('finish_invocation', {'invocation_id': invocation_id, 'result': result, 'worker_id': worker_id, 'error': error})
    except Exception as e:
        sio.emit('finish_invocation', {'invocation_id': invocation_id, 'result': "", 'worker_id': worker_id, 'error': str(e)})

@sio.on('error')
def on_error(data):
    print(data)
    sio.disconnect()

sio.connect(server_url)