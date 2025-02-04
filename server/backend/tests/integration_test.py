import os
import argparse
import subprocess
import requests
import traceback

user_data = {
    'name': 'tested_user',
    'password': 'test_password',
    'email': 'test@lm.clustro_ai.com'
}


class IntegrationTest:
    # BASE_URL = 'http://localhost:5000'  # Set the base URL for the ClustroAI API
    BASE_URL = 'http://api.clustro.ai:5000'
    API_KEY = None  # Set the API_KEY for the ClustroAI

    def __init__(self, base_url=None):
        self.base_url = base_url or self.BASE_URL
        self.user_id = self.create_user()
        self.api_key = self.API_KEY or self.login_user()
        self.model_id = None
        self.worker_id = None
        self.inference_job_id = None

    def create_user(self):
        # Create a user
        user_id = None
        try:
            response = requests.post(f'{self.base_url}/users', json=user_data)
            if response.status_code == 201:
                user_id = response.json()
            else:
                print(f"create_user failed {response.json()}")
        except Exception as e:
            print(f"create_user {str(e)}")
        return user_id

    def login_user(self) -> str:
        api_key = None
        # login user
        try:
            response = requests.post(f'{self.base_url}/login', json=user_data)
            if response.status_code == 200:
                api_key = response.json().get('api_key')
            else:
                print(f"login_user failed {response.json()}")
        except Exception as e:
            print(f"login_user {str(e)}")
        return api_key

    # Helper function to send requests with the API key
    def send_request(self, method, path, data=None):
        try:
            headers = {'X-API-Key': self.api_key}
            response = requests.request(method, f'{self.base_url}/{path}', headers=headers, json=data)
            if response.status_code in (200, 201):
                return response.json()
            else:
                print(response.json())
                return None
        except Exception as e:
            print(str(e))
            return None

    def prepare_data(self):
        # Create a Model
        model_data = {
            "name": "Test_Model",
            "model_type": "text_to_text",
            "version": "7a3e7912c114cec6e833a7afb9a77304b1402926",
            "artifact": "https://github.com/ClustroAI/dummy_model_1_llm",
            "invoke_function": "model_invoke.py/invoke"
        }
        response = self.send_request('POST', 'models', model_data)
        self.model_id = response.get('id') if response else response

        # Update the Model
        update_model_data = {
            'description': 'Updated model description'
        }
        assert self.model_id is not None
        self.send_request('PUT', f'models/{self.model_id}', update_model_data)

        # Get the Model
        response = self.send_request('GET', f'models/{self.model_id}')
        print(f'model info {response}')
        assert response is not None
        assert response.get('description') == 'Updated model description'

        # Create an InferenceJob
        inference_job_data = {
            'model_id': self.model_id,
            'name': 'my-inference-job',
            'set_as_model_default': True
        }
        response = self.send_request('POST', 'inference_jobs', inference_job_data)
        self.inference_job_id = response.get('id') if response else response

        assert self.inference_job_id is not None
        # Update the InferenceJob
        update_inference_job_data = {
            'name': 'updated-inference-job-name',
            'description': 'Updated inference job description'
        }
        self.send_request('PUT', f'inference_jobs/{self.inference_job_id}', update_inference_job_data)

        # Get the InferenceJob
        response = self.send_request('GET', f'inference_jobs/{self.inference_job_id}')
        print(f'InferenceJob {response}')
        assert response is not None
        assert response.get('name') == 'updated-inference-job-name'
        # Create a Worker
        worker_data = {
            'name': 'my-worker',
            'available_gpu': 10
        }
        response = self.send_request('POST', 'workers', worker_data)
        self.worker_id = response.get('id') if response else None

        assert self.worker_id is not None
        # Update the Worker
        update_worker_data = {
            'working_on': self.inference_job_id
        }
        self.send_request('PUT', f'workers/{self.worker_id}', update_worker_data)

        # Get the Worker
        response = self.send_request('GET', f'workers/{self.worker_id}')
        print(f'workers {response}')
        assert response is not None
        assert response.get('working_on') == self.inference_job_id
        # push a async invoke in redis
        self.send_request('POST', f'inference_jobs/{self.inference_job_id}/invoke', data={"input": "Hello World"})
        assert self.inference_job_id is not None
        response = self.send_request('POST', f'models/{self.model_id}/invoke', data={"input": "Model invoke test"})
        print(f'invocation {response}')

    def delete_data(self):
        print("delete_data")
        # Delete everything created for testing
        if self.worker_id:
            self.send_request('DELETE', f'workers/{self.worker_id}')
        if self.inference_job_id:
            self.send_request('DELETE', f'inference_jobs/{self.inference_job_id}')
        if self.model_id:
            self.send_request('DELETE', f'models/{self.model_id}')
        if self.user_id:
            self.send_request('DELETE', f'users/{self.user_id}')

    def start_worker_process(self, local_service_port=8000):
        # start a worker agent
        os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.getcwd()))), 'compute_host'))
        command = [
            'python3',
            'worker_agent.py',
            f'--worker_id={self.worker_id}',
            f'--server_url={self.base_url}',
            f'--local_service_port={local_service_port}'
        ]
        process = subprocess.Popen(command, preexec_fn=os.setsid)
        try:
            process.wait(timeout=20)
        except KeyboardInterrupt:
            # On keyboard interrupt, terminate the subprocess
            process.terminate()
            process.wait()
        except subprocess.TimeoutExpired:
            process.terminate()

    def start_test(self):
        # start integration test
        try:
            self.prepare_data()  # prepare integration test data
            self.start_worker_process()
        except Exception:
            print(traceback.print_exc())

        finally:
            self.delete_data()  # delete integration test data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Python Socket.IO Client for Workers')
    parser.add_argument('--base_url', type=str, default='http://api.clustro.ai:5000',
                        help='base_url')
    args = parser.parse_args()
    IntegrationTest(args.base_url).start_test()
