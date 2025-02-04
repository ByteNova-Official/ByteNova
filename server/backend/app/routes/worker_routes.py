# File: app/routes/worker_routes.py
from flask import Blueprint, request, jsonify, g, current_app
from app.models.worker import Worker
from app.decorators import api_key_required
import string
import random
from app.utils import is_valid_uuid

bp = Blueprint('worker_routes', __name__)

def check_resource_ownership(id):
    if not is_valid_uuid(id):
        return None
    worker = Worker.query.filter_by(id=id).first()
    if worker and worker.user_id == g.user.id:
        return worker
    return None

@bp.route('/', methods=['POST'], strict_slashes=False)
@api_key_required
def create_worker():
    if 'name' in request.json:
        name = request.json.get('name')
    else:
        name = _generate_random_string()
    new_worker = Worker(name, user_id=g.user.id)

    if 'type' in request.json and  request.json.get('type') == 'temp':
        new_worker.type = 'temp'
    else:
        new_worker.type = 'longlive'

    if 'job_assignment_type' in request.json and request.json.get('job_assignment_type') == 'manual':
        new_worker.job_assignment_type = 'manual'
    else:
        new_worker.job_assignment_type = 'auto'

    if 'available_gpu' in request.json:
        new_worker.available_gpu = int(request.json.get('available_gpu'))
    else:
        new_worker.available_gpu = 0

    new_worker.save()
    return jsonify(new_worker.get()), 201

@bp.route('/<string:id>', methods=['GET'], strict_slashes=False)
@api_key_required
def get_worker(id):
    worker = check_resource_ownership(id)
    if not worker:
        current_app.logger.warning("get_worker You are not authorized to access the resource")
        return jsonify({'error': 'You are not authorized to access the resource.'}), 403

    return jsonify(worker.to_dict())

@bp.route('/', methods=['GET'], strict_slashes=False)
@api_key_required
def list_workers():
    workers = g.user.workers
    return jsonify([worker.to_dict() for worker in workers]) 

@bp.route('/<string:id>', methods=['PUT'], strict_slashes=False)
@api_key_required
def update_worker(id):
    worker = check_resource_ownership(id)
    if not worker:
        current_app.logger.warning("update_worker You are not authorized to access the resource")
        return jsonify({'error': 'You are not authorized to access the resource.'}), 403
    
    data = request.get_json()
    if 'working_on' in data:
        worker.working_on = data['working_on']
        if data['working_on'] == "":
            worker.working_on = None
    if 'job_assignment_type' in data:
        worker.job_assignment_type = data['job_assignment_type']
    if 'type' in data:
        worker.type = data['type']

    try:
        worker.save()
        return jsonify(worker.get())
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/<string:id>', methods=['DELETE'], strict_slashes=False)
@api_key_required
def delete_worker(id):
    worker = check_resource_ownership(id)
    if not worker:
        current_app.logger.warning("delete_worker You are not authorized to access the resource")
        return jsonify({'error': 'You are not authorized to access the resource.'}), 403
    worker.delete_from_db()
    return jsonify({'message': 'Worker deleted'})

def _generate_random_string(length=8):
    characters = string.ascii_lowercase + string.digits  # includes lowercase letters and numbers
    return ''.join(random.choice(characters) for _ in range(length))