# File: app/routes/model_routes.py
import time
from flask import Blueprint, request, jsonify, g, current_app
from app.models.model import Model
from app.models.invocation import Invocation
from app.models.inference_job import InferenceJob
from app.models.worker import Worker
from app.decorators import api_key_required
from app import db
from app.utils import is_valid_uuid
from app.invoke_utils import check_and_scale_inference_job_workers, inference_job_heartbeat

bp = Blueprint('model_routes', __name__)
api_limit_per_min = 30


def check_resource_ownership(id):
    if not is_valid_uuid(id):
        return None
    model = Model.query.filter_by(id=id).first()
    if model and model.user_id == g.user.id:
        return model
    return None


def check_resource_ownership_public_read(id):
    if not is_valid_uuid(id):
        return None
    model = Model.find(id)
    if model and (model.user_id == g.user.id or model.visibility == 'public'):
        return model
    return None


@bp.route('/', methods=['POST'], strict_slashes=False)
@api_key_required
def create_model():
    user_id = g.user.id
    # Check if required fields are in JSON payload
    if not all(key in request.json for key in ['name', 'model_type', 'artifact', 'version']):
        current_app.logger.warning(
            "create_model Missing required fields. 'name', 'model_type', 'artifact', and 'version' are required")
        return jsonify(
            {"error": "Missing required fields. 'name', 'model_type', 'artifact', and 'version' are required."}), 400
    name = request.json.get('name')
    model_type = request.json.get('model_type')
    artifact = request.json.get('artifact')
    version = request.json.get('version')
    new_model = Model(name, user_id, model_type, artifact, version)

    if 'invoke_function' in request.json:
        new_model.invoke_function = request.json.get('invoke_function')
    if 'runtime_docker_image' in request.json:
        new_model.runtime_docker_image = request.json.get('runtime_docker_image')
    if 'example_input' in request.json:
        new_model.example_input = request.json.get('example_input')
    if 'description' in request.json:
        new_model.description = request.json.get('description')
    if 'visibility' in request.json:
        new_model.visibility = request.json.get('visibility')
    if 'required_gpu' in request.json:
        new_model.required_gpu = request.json.get('required_gpu')

    try:
        if Model.find_by_name(user_id, name) != None:
            current_app.logger.warning("Model name already existed")
            return jsonify({'error': "Model name already existed"}), 400
        new_model.save()
        return jsonify(new_model.get()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/<string:id>', methods=['GET'], strict_slashes=False)
@api_key_required
def get_model(id):
    model = check_resource_ownership_public_read(id)
    if not model:
        current_app.logger.warning("You are not authorized to access the resource.")
        return jsonify({'error': 'You are not authorized to access the resource.'}), 403
    return jsonify(model.get())


@bp.route('/<string:id>', methods=['PUT'], strict_slashes=False)
@api_key_required
def update_model(id):
    model = check_resource_ownership(id)
    if not model:
        current_app.logger.warning("update_model You are not authorized to access the resource.")
        return jsonify({'error': 'You are not authorized to access the resource.'}), 403

    visiblity_changed = False

    data = request.get_json()
    if 'model_type' in data:
        model.model_type = data['model_type']
    if 'version' in data:
        model.version = data['version']
    if 'artifact' in data:
        model.artifact = data['artifact']
    if 'invoke_function' in data:
        model.invoke_function = data['invoke_function']
    if 'runtime_docker_image' in data:
        model.runtime_docker_image = data['runtime_docker_image']
    if 'example_input' in data:
        model.example_input = data['example_input']
    if 'description' in data:
        model.description = data['description']
    if 'required_gpu' in data:
        model.required_gpu = data['required_gpu']
    if 'visibility' in data:
        if model.visibility != data['visibility']:
            visiblity_changed = True
        model.visibility = data['visibility']
    try:
        model.save()
        # Update all Inference Jobs of a Model when visibility changes
        if visiblity_changed:
            for ij in model.inference_jobs:
                ij.visibility = model.visibility
                db.session.add(ij)
            db.session.commit()
        return jsonify(model.get())
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/', methods=['GET'], strict_slashes=False)
@api_key_required
def list_models():
    models = Model.query.filter((Model.visibility == "public") | (Model.user_id == g.user.id)).all()
    return jsonify([model.get_item_for_list() for model in models])


@bp.route('/<string:id>', methods=['DELETE'], strict_slashes=False)
@api_key_required
def delete_model(id):
    model = check_resource_ownership(id)
    if not model:
        current_app.logger.warning("delete_model You are not authorized to access the resource.")
        return jsonify({'error': 'You are not authorized to access the resource.'}), 403

    model.delete_from_db()
    return jsonify({'message': 'Model deleted'})


@bp.route('/<string:id>/invoke', methods=['POST'], strict_slashes=False)
@api_key_required
def model_invoke_inference_job(id):
    """
    model invoke default_inference_job
    @param id model id
    """
    model = check_resource_ownership(id)
    if not model:
        current_app.logger.warning('You are not authorized to access the resource')
        return jsonify({'error': 'You are not authorized to access the resource.'}), 403

    if not request.json.get('input'):
        current_app.logger.warning("Missing required fields. 'input' are required.")
        return jsonify({"error": "Missing required fields. 'input' are required."}), 400

    if not model.default_inference_job:  # when not exist default_inference_job raise exception
        current_app.logger.warning('model miss default_inference_job')
        return jsonify({'error': 'model miss default_inference_job'}), 404

    if Invocation.count_user_invocations_last_min(g.user.id) > api_limit_per_min:
        current_app.logger.warning('API limit exceeded.')
        return jsonify({'error': 'API limit exceeded.'}), 429

    inference_job_id = model.default_inference_job
    inference_job = InferenceJob.find_by_id(inference_job_id)
    if not inference_job:
        current_app.logger.warning('default inference job not found')
        return jsonify({'error': 'default inference job not found'}), 404

    invocation = generate_invocation(model, inference_job)
    return jsonify({'invocation_id': invocation.id}), 201


@bp.route('/<string:id>/invoke_sync', methods=['POST'], strict_slashes=False)
@api_key_required
def model_invoke_inference_job_sync(id):
    model = check_resource_ownership(id)
    if not model:
        current_app.logger.warning('You are not authorized to access the resource')
        return jsonify({'error': 'You are not authorized to access the resource.'}), 403

    if not request.json.get('input'):
        current_app.logger.warning("Missing required fields. 'input' are required.")
        return jsonify({"error": "Missing required fields. 'input' are required."}), 400

    if not model.default_inference_job:  # when not exist default_inference_job raise exception
        current_app.logger.warning('model miss default_inference_job')
        return jsonify({'error': 'model miss default_inference_job'}), 404

    if Invocation.count_user_invocations_last_min(g.user.id) > api_limit_per_min:
        current_app.logger.warning('API limit exceeded.')
        return jsonify({'error': 'API limit exceeded.'}), 429

    inference_job_id = model.default_inference_job
    inference_job = InferenceJob.find_by_id(inference_job_id)  # find the job if it not exists maybe job is deleted
    if not inference_job:
        current_app.logger.warning('default inference job not found')
        return jsonify({'error': 'default inference job not found'}), 404

    invocation = generate_invocation(model, inference_job)

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


def generate_invocation(model: Model, inference_job: InferenceJob) -> Invocation:
    inference_job_id = str(model.default_inference_job)
    invocation = Invocation(inference_job_id=inference_job_id, user_id=g.user.id)
    invocation.input = request.json.get('input')
    invocation.save()
    # Enqueue the invocation to the job's queue
    current_app.logger.info(f"inference_job_id {inference_job_id}")
    current_app.r.lpush(f'job:{inference_job_id}', str(invocation.id))
    check_and_scale_inference_job_workers(inference_job)
    inference_job_heartbeat(inference_job)
    return invocation

