import argparse
import utils
import subprocess
import sys
import os

parser = argparse.ArgumentParser(description='Python Socket.IO Client for Host agent')
parser.add_argument('--server_url', type=str, default='http://api.clustro.ai:5000',
                    help='backend server url')
parser.add_argument('--local_service_port', type=str, default='8000',
                    help='local server port')
parser.add_argument('--gpu_limit', type=str, help='GPU limit override', default='999')
args = parser.parse_args()
SERVER_URL = args.server_url
LOCAL_SERVICE_PORT = args.local_service_port
gpu_limit_override = args.gpu_limit
if "CLUSTROAI_API_KEY" not in os.environ:
    print("Error: CLUSTROAI_API_KEY must be set in environment variables.")
    sys.exit(1)

def start_worker_process(worker_id, local_service_port):
    command = [
        'python3', 
        'worker_agent.py', 
        f'--worker_id={worker_id}', 
        f'--server_url={SERVER_URL}', 
        f'--local_service_port={local_service_port}'
    ]
    process = subprocess.Popen(command, preexec_fn=os.setsid)
    try:
        process.wait()
    except KeyboardInterrupt:
        # On keyboard interrupt, terminate the subprocess
        process.terminate()
        process.wait()

if "CLUSTROAI_WORKER_ID" in os.environ:
    start_worker_process(os.environ["CLUSTROAI_WORKER_ID"], LOCAL_SERVICE_PORT)
else:
    # TODO: Create multiple workers with GPU limit
    print("CLUSTROAI_WORKER_ID not found. Creating a temporary worker...")
    worker_sys_info = utils.get_system_info()
    available_gpu = min(worker_sys_info['gpu_memory_gb'], int(gpu_limit_override))
    worker_id = utils.create_temp_worker(api_key=os.environ["CLUSTROAI_API_KEY"], available_gpu=available_gpu, api_url= SERVER_URL)
    start_worker_process(worker_id, LOCAL_SERVICE_PORT)
