import os
import subprocess
import requests
import shutil
import string
import random

MODEL_DIR = 'model_repo'
APP_TEMPLATE_NAME = 'flask_app.py.template'

def get_system_info():
    # Get GPU information using nvidia-smi
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader,nounits'], stdout=subprocess.PIPE)
        gpu_info = result.stdout.decode('utf-8').strip().split('\n')[0]
        gpu_name, gpu_memory = gpu_info.split(', ')
    except Exception as e:
        gpu_name, gpu_memory = "N/A", "N/A"
    
    if gpu_memory == "N/A":
        gpu_memory_gb = 0
    else:
        gpu_memory_gb = int(int(gpu_memory)/1024)
    
    # Get free disk space
    st = os.statvfs('/')
    free_disk_gb = int(st.f_bavail * st.f_frsize / (1024**3))
    
    # Get external IP using requests
    try:
        response = requests.get('http://ifconfig.me', timeout=10)
        response.raise_for_status()  # Raises an exception for HTTP errors
        ip = response.text.strip()
    except Exception as e:
        ip = "N/A"

    return {"gpu_name": gpu_name, "gpu_memory_gb": gpu_memory_gb, "free_disk_gb": free_disk_gb, "ip": ip}

def get_inference_job_id(worker_id, api_key):
    worker_info = get_worker(worker_id, api_key)
    return worker_info['working_on']

def _get_resource(endpoint, api_key):
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': api_key
    }
    url = f"https://console.clustro.ai{endpoint}"
    response = requests.get(url, headers=headers)
    # Check if the request was successful
    response.raise_for_status()
    return response.json()

def get_worker(worker_id, api_key):
    return _get_resource(f"/api/workers/{worker_id}", api_key)

def get_inference_job(job_id, api_key):
    return _get_resource(f"/api/inference_jobs/{job_id}", api_key)

def get_model(model_id, api_key):
    return _get_resource(f"/api/models/{model_id}", api_key)

def get_model_from_worker(worker_id, api_key):
    worker = get_worker(worker_id, api_key)
    if worker['working_on'] is None:
        return None
    job = get_inference_job(worker['working_on'], api_key)
    model = get_model(job['model_id'], api_key)
    return model

def get_model_repo(url, sha, model_invoke_function):
    if not os.path.exists(MODEL_DIR):
        os.mkdir(MODEL_DIR)
    model_file_name = get_model_file_path(url, sha)
    if os.path.exists(model_file_name):
        print("Model repo already prepared")
        return model_file_name
    # Clone the repository from the provided URL directly into 'model_repo'
    subprocess.run(['git', 'clone', url, model_file_name], check=True)
    subprocess.run(['git', '-C', model_file_name, 'checkout', sha], check=True)
    # TODO; prepare virtual env for package dependencies
    package, function = model_invoke_function.split('/')
    package_name = package.split('.py')[0]
    # Read the contents of flask_app.py.template
    with open('flask_app.py.template', 'r') as file:
        lines = file.readlines()
    lines[0] = f"from {package_name} import {function} as invoke\n"
    # Write the modified content to a new file flask_app.py
    with open('flask_app.py', 'w') as file:
        file.writelines(lines)
    shutil.copy2('flask_app.py', model_file_name)
    return model_file_name

def get_model_file_path(url, sha):
    model_file_name = MODEL_DIR + "/" + _get_repo_name_from_url(url) + "_" + sha
    return model_file_name

def _get_repo_name_from_url(url):
    # Split the URL by the slashes
    parts = url.rstrip('/').split('/')
    # Return the last part, which is usually the repo name
    return parts[-1].replace('.git', '')

def _generate_random_string(length=8):
    characters = string.ascii_lowercase + string.digits  # includes lowercase letters and numbers
    return ''.join(random.choice(characters) for _ in range(length))

def create_temp_worker(api_key, name=_generate_random_string(), available_gpu=0, type='temp', job_assignment_type='auto', api_url = "https://api.clustro.ai/api"):
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': api_key
    }
    url = f"{api_url}/workers/"
    payload = {
        'name': name,
        'type': type,
        'job_assignment_type': job_assignment_type,
        'available_gpu': available_gpu
    }
    response = requests.post(url, headers=headers, json=payload)
    # Check if the request was successful
    response.raise_for_status()
    return response.json()["id"]