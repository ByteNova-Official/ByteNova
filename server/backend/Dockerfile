FROM python:3.9.9-slim-buster
WORKDIR /
COPY requirements.txt .
RUN python3 -m ensurepip --upgrade
RUN pip install -r requirements.txt
COPY . .
# CMD ["sh", "-c", "FLASK_ENV=production gunicorn -w 1 -b 0.0.0.0:5000 run:app --timeout 3600"]
CMD ["sh", "-c", "FLASK_ENV=production python run.py"]
