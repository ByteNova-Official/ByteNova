# ByteNovaAI

## Table of Contents

* [Official Website](#Official-Website)
* [Quick Start](#Quick-Start)
* [Run Tests](#Run-Tests)
* [SocketIO](#SocketIO)
* [Scheduled Tasks](#Scheduled-Tasks)

## Official Website
[clustro.ai](https://www.clustro.ai/)

[console.clustro.ai](https://console.clustro.ai/)

[user docs](https://docs.clustro.ai/)


## Quick Start

### compute_host
compute_host is a process based on SocketIO communication. By starting the host_agent, the machine will be registered as a real worker. Subsequent jobs can be assigned and executed for this worker.

#### Local Run
Install dependencies
```bash
pip install -r requirements.txt
export CLUSTROAI_API_KEY=Your APi KEY
```
Run host_agent, it will create a temporary worker and communicate with the server.

There are three optional arguments:
1. --server_url   default  http://api.clustro.ai:5000
2. --local_service_port default 8000
3. --gpu_limit default 999
```python
python host_agent.py
```

#### Start with Docker
```bash
docker build -t host_agent:v1 .
docker run -d -e CLUSTROAI_API_KEY=Your APi KEY host_agent:v1
```

### server
Under server, there are backend, frontend, and landingPage.

* backend is the project backend, primarily designed with technologies such as flask, postgres, and redis.
* frontend is the frontend project primarily designed with technologies like react, umijs/max, and ant-design.
* landingPage is the old frontend project, which will be phased out over time and can be ignored.
#### backend
##### Local Start
You need to have a postgres database and redis. It's recommended to install locally using Docker.
```bash
docker pull postgres
docker run -d --name=postgres -e POSTGRES_PASSWORD=your password -p 5432:5432 postgres
docker pull redis
docker run -d --name=redis  -p 6379:6379 redis

export DB_USER=postgres
export DB_PASSWORD=your password  
export DB_HOST=localhost
python run.py
```

##### Start with Docker
```bash
docker build -t backend:v1 .
docker run -d -e DB_USER=postgres,DB_PASSWORD=your password,DB_HOST=localhost backend:v1
```

#### frontend
Configure environment variables:
```bash
cp env_template .env
Modify REACT_APP_BACKEND_SERVER_URL to your backend's starting URL.
```
##### Local Start
```bash
npm install 
npm run start
```
##### Start with Docker
```bash
docker-compose up -d frontend
```
Visit URL http://localhost:3000 to view the page.

## Run Tests
```bash
# Run all test cases
DB_USER=postgres DB_PASSWORD=your password pytest
# Run a single test case
DB_USER=postgres DB_PASSWORD=your password pytest tests/test_worker_routes.py::test_update_worker
```

## SocketIO
When the backend starts, it launches a SocketIO server. When worker_agent starts, it connects to the backend's SocketIO and creates a namespace for communication. This facilitates the allocation of the inference job to this worker. The specific process is as follows:
1. worker_agent connects to the SocketIO server and initiates communication.
2. The SocketIO server sends a request_worker_id request.
3. worker_agent sends a provide_worker_id request.
4. The SocketIO server sends a worker_session_established request.
5. worker_agent initiates a request to start communication.
6. The SocketIO server sends prepare_model. At this point, the worker_agent begins to clone code from the git repository and starts the Flask app.
7. The inference job is assigned to worker_agent.
8. worker_agent begins execute_invocation and sends the results back to the SocketIO server.

## Scheduled Tasks
1. job_matching automatically assigns inference jobs to available idle workers.
2. The auto_scaler periodically scans the inference job, ensuring that workers that have completed their jobs are in an idle state.
