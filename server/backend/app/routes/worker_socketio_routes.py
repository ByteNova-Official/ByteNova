# File: app/routes/worker_socketio_routes.py

from flask import session, current_app
from app.models.worker import Worker
from app.models.inference_job import InferenceJob
from app.models.invocation import Invocation
from app.utils import create_presigned_fields
from flask_socketio import emit
import time
from app import app, socketio, db  # import the socketio instance
from datetime import datetime, timedelta
import json

@socketio.on('connect')
def on_connect():
    current_app.logger.info('Client connected')
    session['alive'] = True
    session['model_deployed'] = False
    session['target_model'] = None
    session['worker_refresh_at'] = None
    emit('request_worker_id', {'data': 'Please provide worker id.'})

@socketio.on('disconnect')
def on_disconnect():
    session['alive'] = False
    if session.get('worker_id'):
        worker = Worker.query.filter_by(id=session['worker_id']).first()
        if worker.type == "temp":
            worker.delete_from_db()
        else:
            worker.connected = False
            worker.status = "IDLE"
            worker.info = None
            if worker.job_assignment_type == "auto":
                worker.working_on = None
            worker.save()
    if session.get('working_on_invocation'):
        invocation = Invocation.query.filter_by(id=session['working_on_invocation']).first()
        if invocation:
            invocation.enqueue()

@socketio.on('provide_worker_id')
def on_provide_worker_id(data):
    # Query the database for a worker with the provided id
    try:
        worker = Worker.query.filter_by(id=data['id']).first()
    except:
        emit('error', {'message': f"No worker id found."})
        return
    # If a worker was found, store the id in the session
    if worker is not None:
        session['worker_id'] = data['id']
        worker_info = {
            'gpu_name': data['gpu_name'],
            'gpu_memory_gb': data['gpu_memory_gb'],
            'free_disk_gb': data['free_disk_gb'],
            'ip': data['ip'],
        }
        worker.info = json.dumps(worker_info)
        worker.connected = True
        db.session.add(worker)
        db.session.commit()
        emit('worker_session_established', {'message': f"Worker  with id {data['id']} session established."})
    else:
        # Handle the case where no worker was found with the provided id
        # You could emit an error message back to the client, log an error, etc.
        current_app.logger.warning(f"No worker found with id {data['id']}")
        emit('error', {'message': f"No worker found with id {data['id']}"})

@socketio.on('finish_invocation')
def on_finish_invocation(data):
    invocation_id = data['invocation_id']
    worker_id = data['worker_id']
    worker = Worker.query.filter_by(id=worker_id).first()
    if worker.connected == False:
        worker.connected = True
        worker.save()

    invocation = Invocation.query.filter_by(id=invocation_id).first()
    invocation.status = 'COMPLETED'
    invocation.processed_by_worker_id = worker_id
    if 'error' in data and len(data['error']) > 0:
        invocation.error = data['error']
        invocation.status = 'FAILED'
    invocation.result = data['result']
    invocation.process_finish_time = datetime.utcnow()
    db.session.add(invocation)
    db.session.commit()
    current_app.logger.info(f'invocation {invocation_id} finished by worker {worker.name}!')
    session[invocation_id] = 'COMPLETED'
    session['working_on_invocation'] = None
    # Write the result to the database

@socketio.on('finish_model_deployment')
def on_finish_model_deployment(data):
    session['model_deployed'] = data['model_artifact']
    worker = Worker.query.filter_by(id=session['worker_id']).first()
    worker.connected = True
    worker.status = "SERVING"
    worker.save()

@socketio.on('model_deployment_failed')
def on_model_deployment_failed(data):
    worker = Worker.query.filter_by(id=session['worker_id']).first()
    error = ""
    if "error" in data:
        error = data["error"]
    worker.recent_deployment_failure = f'InferenceJob {worker.working_on} with repo {data["model_artifact"]} failed to deploy. Error: {error}'
    worker.working_on = None
    worker.status = "IDLE"
    worker.save()

@socketio.on('start')
def start():
    worker_id = session.get('worker_id')
    if not worker_id:
        emit('error', {'message': f"No worker ID provided."})
        return

    worker = Worker.query.filter_by(id=worker_id).first()
    if not worker:
        emit('error', {'data': 'worker not found'})
        return

    while session['alive']:
        while not worker.working_on:
            if not session['alive']: return
            emit('message', {'data': 'no job assigned yet...'})
            time.sleep(5)
            worker.refresh()

        # Check the datetime stamp in session['worker_refresh_at']
        last_refresh_time = session.get('worker_refresh_at')
        if last_refresh_time:
            # Assuming the stored datetime is in the format 'YYYY-MM-DD HH:MM:SS', adjust if different
            last_refresh_time = datetime.strptime(last_refresh_time, '%Y-%m-%d %H:%M:%S')

            # If more than 2 seconds has passed
            if datetime.now() - last_refresh_time > timedelta(seconds=2):
                worker.refresh()
                if not worker.working_on:
                    session['model_deployed'] = None
                    continue
                model = InferenceJob.find_by_id(worker.working_on).get_model()
                session['worker_refresh_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        else:
            worker.refresh()
            if not worker.working_on:
                session['model_deployed'] = None
                continue
            model = InferenceJob.find_by_id(worker.working_on).get_model()
            session['worker_refresh_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if not session['model_deployed'] or (session['model_deployed'] != model.artifact):
            session['model_deployed'] = None
            inference_job = InferenceJob.find_by_id(worker.working_on)
            emit('prepare_model', {'model_artifact': model.artifact, 'model_invoke_function': inference_job.model_invoke_function, 'model_version': inference_job.model_version})
            worker.status = "LOADING_MODEL"
            worker.connected = True
            worker.save()
            while not session['model_deployed']:
                if not session['alive']: return
                # Waiting for finish_model_deployment from the host agent
                time.sleep(0.1)
                pass
            emit('message', {'data': f'Job {worker.working_on} is assigned to the worker. Waiting for new tasks.'})

        redis_tasks_len = app.r.llen(f'job:{worker.working_on}')
        if redis_tasks_len != 0:
            emit('message', {'data': f'Job {worker.working_on} is assigned to the worker. With {redis_tasks_len} tasks in the queue.'})
        if redis_tasks_len != 0:
            invocation_id = app.r.lpop(f'job:{worker.working_on}')
            if invocation_id:
                invocation_id = invocation_id.decode('utf-8')
                invocation = Invocation.query.filter_by(id=invocation_id).first()
                invocation.status = 'PROCESSING'
                invocation.processed_by_worker_id = worker_id
                invocation.processed_by_user = worker.user_id
                invocation.process_start_time = datetime.utcnow()
                invocation.save()
                model = invocation.get_inference_job().get_model()
                if model.model_type == "text_to_image":
                    s3_upload_fields = create_presigned_fields(invocation_id)
                    emit('execute_invocation', {'invocation_id': invocation_id, 'input': invocation.input, 's3_upload_fields': s3_upload_fields})
                else:
                    emit('execute_invocation', {'invocation_id': invocation_id, 'input': invocation.input})
                session['working_on_invocation'] = invocation_id
                session[invocation_id] = 'WORKING'
                while session[invocation_id] == 'WORKING':
                    if not session['alive']: return
                    # time.sleep(1)
                    time.sleep(0.1)
                    # print(f'waiting for invocation {invocation_id} to finish')
                    pass
    time.sleep(0.1)
