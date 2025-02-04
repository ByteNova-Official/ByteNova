# File: app/routes/inference_job_routes.py
from flask import Blueprint, jsonify, request, g, current_app
from app import db
from app.models.inference_job import InferenceJob
from app.models.worker import Worker
from app.models.invocation import Invocation
from app.models.model import Model
from app.utils import is_valid_uuid
from app import app
import time
from app.decorators import api_key_required
from app.invoke_utils import check_and_scale_inference_job_workers, inference_job_heartbeat

public_inference_job_map = {
    "falcon_7b_instruct": "36e7372c-514d-425f-9ef0-5120b9ca1e8b",
    "falcon_7b": "ee1ffcb4-d1fb-4955-9417-5b8e7f6d9b2c",
    "stable_diffusion_2_1": "5ee9fb5a-3cfc-47b4-abc3-aa8411b41b21",
}

api_limit_per_min = 30


def check_resource_ownership_public_read(id):
    if not is_valid_uuid(id):
        return None
    if id in public_inference_job_map.keys():
        id = public_inference_job_map[id]
        inference_job = InferenceJob.query.filter_by(id=id).first()
        return inference_job
    inference_job = InferenceJob.query.filter_by(id=id).first()
    if inference_job and (inference_job.user_id == g.user.id or inference_job.visibility == 'public'):
        return inference_job
    return None


def check_resource_ownership(id):
    if not is_valid_uuid(id):
        return None
    if id in public_inference_job_map.keys():
        id = public_inference_job_map[id]
        inference_job = InferenceJob.query.filter_by(id=id).first()
        return inference_job
    inference_job = InferenceJob.query.filter_by(id=id).first()
    if inference_job and (inference_job.user_id == g.user.id):
        return inference_job
    return None


bp = Blueprint('inference_job_routes', __name__)


@bp.route('/', methods=['POST'], strict_slashes=False)
@api_key_required
def create_inference_job():
    # Check if 'model_id' and 'name' are in JSON payload
    if not all(key in request.json for key in ['model_id', 'name']):
        current_app.logger.warning("Missing required fields. 'model_id' and 'name' are required.")
        return jsonify({"error": "Missing required fields. 'model_id' and 'name' are required."}), 400

    # Fetch the model from the database
    model = Model.query.filter_by(id=request.json.get('model_id')).first()
    if not model:
        current_app.logger.warning(f"{request.json.get('model_id')} Model not found")
        return jsonify({'error': 'Model not found'}), 404

    # Initialize the new InferenceJob object
    name = request.json['name']
    model_id = model.id
    user_id = g.user.id
    new_job = InferenceJob(
        name=name,
        model_id=model_id,
        user_id=user_id,
        # set other default values if needed
    )

    # Assign optional fields to the object if they exist in request.json
    if 'status' in request.json:
        new_job.status = request.json['status']
    if 'description' in request.json:
        new_job.description = request.json['description']
    if 'min_workers' in request.json:
        new_job.min_workers = request.json['min_workers']
    if 'max_workers' in request.json:
        new_job.max_workers = request.json['max_workers']
    if 'desired_workers' in request.json:
        new_job.desired_workers = request.json['desired_workers']

    # Sync other info from model, if necessary
    new_job.sync_info_from_model()
    if request.json.get('set_as_model_default') is True:
        model.default_inference_job = new_job.id
        model.save_db_no_commit()

    # Save the new job
    try:
        new_job.save()
        return jsonify(new_job.get()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/<string:id>', methods=['GET'], strict_slashes=False)
@api_key_required
def get_inference_job(id):
    inference_job = check_resource_ownership_public_read(id)
    if not inference_job:
        current_app.logger.warning('You are not authorized to access the resource')
        return jsonify({'error': 'You are not authorized to access the resource.'}), 403

    return jsonify(inference_job.to_dict())


@bp.route('/', methods=['GET'], strict_slashes=False)
@api_key_required
def list_inference_jobs():
    model_id = request.args.get('model_id')
    if model_id:
        if not is_valid_uuid(model_id):
            current_app.logger.warning(f'{model_id} Invalid Model ID')
            return jsonify({'error': 'Invalid Model ID'}), 400
        model = Model.find(model_id)
        jobs = []
        if model:
            jobs = model.inference_jobs
    else:
        jobs = InferenceJob.query.filter(
            (InferenceJob.visibility == "public") | (InferenceJob.user_id == g.user.id)).all()
    return jsonify([job.get_item_for_list() for job in jobs]), 200


@bp.route('/<string:id>', methods=['PUT'], strict_slashes=False)
@api_key_required
def update_inference_job(id):
    job = check_resource_ownership(id)  # Ensure this function is applicable for inference_jobs as well
    if not job:
        current_app.logger.warning('You are not authorized to access the resource')
        return jsonify({'error': 'You are not authorized to access the resource.'}), 403

    data = request.get_json()

    if 'name' in data:
        job.job_name = data['name']
    if 'job_assignment_type' in data:
        job.job_assignment_type = data['job_assignment_type']
    if 'scaling_type' in data:
        job.scaling_type = data['scaling_type']
    if 'min_workers' in data:
        job.min_workers = data['min_workers']
    if 'max_workers' in data:
        job.max_workers = data['max_workers']
    if 'desired_workers' in data:
        job.desired_workers = data['desired_workers']
    if 'status' in data:
        job.status = data['status']
    if 'enabled' in data:
        job.enabled = bool(data['enabled'])  # Cast to boolean
    if 'description' in data:
        job.description = data['description']

    job.save()
    return jsonify(job.to_dict()), 200


@bp.route('/<string:id>', methods=['DELETE'], strict_slashes=False)
@api_key_required
def delete_inference_job(id):
    inference_job = check_resource_ownership(id)
    if not inference_job:
        current_app.logger.warning('You are not authorized to access the resource')
        return jsonify({'error': 'You are not authorized to access the resource.'}), 403
    inference_job.delete_from_db()
    return jsonify({'message': 'Inference Job deleted'}), 200


@bp.route('/<string:id>/invoke', methods=['POST'], strict_slashes=False)
# @api_key_required_with_exception(allowed_ids=public_inference_job_map.keys())
@api_key_required
def invoke_inference_job(id):
    inference_job = check_resource_ownership_public_read(id)
    if not inference_job:
        current_app.logger.warning('You are not authorized to access the resource')
        return jsonify({'error': 'You are not authorized to access the resource.'}), 403
    if hasattr(g, 'user'):
        user_id = g.user.id
    else:
        user_id = inference_job.user_id
    if id in public_inference_job_map.keys():
        id = public_inference_job_map[id]
    if Invocation.count_user_invocations_last_min(user_id) > api_limit_per_min:
        current_app.logger.warning('API limit exceeded.')
        return jsonify({'error': 'API limit exceeded.'}), 429
    invocation = Invocation(inference_job_id=id, user_id=user_id)
    invocation.input = request.json.get('input')
    invocation.save_to_db()

    # Enqueue the invocation to the job's queue
    app.r.lpush(f'job:{id}', str(invocation.id))
    check_and_scale_inference_job_workers(inference_job)
    inference_job_heartbeat(inference_job)

    return jsonify({'invocation_id': invocation.id}), 201


@bp.route('/<string:id>/invoke_sync', methods=['POST'], strict_slashes=False)
# @api_key_required_with_exception(allowed_ids=public_inference_job_map.keys())
@api_key_required
def invoke_inference_job_sync(id):
    inference_job = check_resource_ownership_public_read(id)
    if not inference_job:
        current_app.logger.warning('You are not authorized to access the resource')
        return jsonify({'error': 'You are not authorized to access the resource.'}), 403
    if hasattr(g, 'user'):
        user_id = g.user.id
    else:
        user_id = inference_job.user_id
    if id in public_inference_job_map.keys():
        id = public_inference_job_map[id]
    if Invocation.count_user_invocations_last_min(user_id) > api_limit_per_min:
        current_app.logger.warning('API limit exceeded.')
        return jsonify({'error': 'API limit exceeded.'}), 429
    invocation = Invocation(inference_job_id=id, user_id=user_id)
    invocation.input = request.json.get('input')
    invocation.save_to_db()
    # Enqueue the invocation to the job's queue
    app.r.lpush(f'job:{id}', str(invocation.id))
    check_and_scale_inference_job_workers(inference_job)
    inference_job_heartbeat(inference_job)

    status = 'ENQUEUED'
    while status != 'COMPLETED':
        # Re-fetch the invocation from the database
        # db.session.expire(invocation)
        db.session.refresh(invocation)
        invocation = Invocation.query.get(invocation.id)
        status = invocation.status
        time.sleep(0.5)
    worker = Worker.query.filter_by(id=invocation.processed_by_worker_id).first()
    return jsonify({
        'invocation_id': invocation.id,
        'result': invocation.result,
        'processed_by_worker': worker.name,
        'created_at': invocation.created_at,
        'process_start_time': invocation.process_start_time,
        'process_finish_time': invocation.process_finish_time,
    }), 201
