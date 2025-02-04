# Use the specified NVIDIA CUDA base image
FROM nvidia/cuda:11.6.2-runtime-ubuntu20.04

# Set the working directory
WORKDIR /app

# Copy the specified files to the container
COPY host_agent.py .
COPY fake_inference_app.py .
COPY requirements.txt .
COPY utils.py .
COPY flask_app.py.template .
COPY worker_agent.py .

# Install python3, pip, and git
RUN apt update && apt install -y \
    python3 \
    python3-pip \
    git \
    lsof

RUN export DEBIAN_FRONTEND=noninteractive && apt-get update -q && apt-get install -yq ffmpeg libsm6 libxext6

# Install the Python requirements
RUN pip3 install -r requirements.txt

CMD ["python3", "host_agent.py"]
