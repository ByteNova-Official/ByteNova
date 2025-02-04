# File: tests/test_inference_job_routes.py
import redis
import pytest
from flask import json
from app import create_app, db
from app.models.user import User
from app.models.inference_job import InferenceJob
from app.models.invocation import Invocation
from app.models.model import Model
from tests.test_model_routes import random_email


@pytest.fixture(scope='module')
def client():
    flask_app = create_app('config.TestingConfig')
    flask_app.r = redis.Redis(host=flask_app.config['REDIS_HOST'], port=6379, db=0)
    from app.routes import user_routes
    flask_app.register_blueprint(user_routes.bp, url_prefix='/users')

    from app.routes import inference_job_routes
    flask_app.register_blueprint(inference_job_routes.bp, url_prefix='/inference_jobs')

    # Register other required routes

    testing_client = flask_app.test_client()
    with flask_app.app_context():
        db.create_all()
    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()


@pytest.fixture
def job_data():
    return {
        'job_name': 'Test Job',
        'job_status': 'ENQUEUED',
        'enabled': True,
    }


@pytest.fixture
def user_data():
    email = random_email()
    return {
        'name': 'Test User',
        'email': email,
        'password': 'password123',
        'phone': '1234567890',
        'company': 'Test Company'
    }


@pytest.fixture
def created_user(client, user_data):
    response = client.post('/users', json=user_data)
    assert response.status_code == 201
    user_id = response.get_json()
    model = Model(name='Test_Model',
                  user_id=user_id,
                  model_type='text_to_text',
                  version='7a3e7912c114cec6e833a7afb9a77304b1402926',
                  artifact='https://github.com/ClustroAI/dummy_model_1_llm',
                  invoke_function='model_invoke.py/invoke')
    model.save()
    user = db.session.get(User, user_id)
    assert user is not None

    yield user

    # Clean up the created user
    user.delete_from_db()
    db.session.commit()


@pytest.fixture
def created_inference_job(client, created_user, job_data):
    headers = {'X-API-Key': created_user.api_keys[0].key}
    job_data['model_id'] = created_user.models[0].id
    job_data['name'] = created_user.models[0].name
    response = client.post('/inference_jobs', json=job_data, headers=headers)
    assert response.status_code == 201
    job_id = response.get_json().get('id')

    job = db.session.get(InferenceJob, job_id)
    assert job is not None

    yield job

    # Clean up the created job
    job.delete_from_db()
    db.session.commit()


def test_create_delete_job(client, created_user, job_data):
    headers = {'X-API-Key': created_user.api_keys[0].key}
    job_data['model_id'] = created_user.models[0].id
    job_data['name'] = created_user.models[0].name
    response = client.post('/inference_jobs', json=job_data, headers=headers)
    assert response.status_code == 201
    job_id = response.get_json().get('id')

    job = db.session.get(InferenceJob, job_id)
    assert job is not None
    assert job.job_name == 'Test_Model'

    response = client.delete(f'/inference_jobs/{job_id}', headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Inference Job deleted'
    response = client.get(f'/inference_jobs/{job_id}', headers=headers)
    assert response.status_code == 403
    data = response.get_json()
    assert data['error'] == 'You are not authorized to access the resource.'


def test_get_inference_job(client, created_inference_job):
    response = client.get(f'/inference_jobs/{created_inference_job.id}',
                          headers={'X-API-Key': created_inference_job.user.api_keys[0].key})
    assert response.status_code == 200
    inference_job_data = response.get_json()
    assert inference_job_data['id'] == str(created_inference_job.id)
    assert inference_job_data['name'] == 'Test_Model'


def test_update_inference_job(client, created_inference_job):
    response = client.get(f'/inference_jobs/{created_inference_job.id}',
                          headers={'X-API-Key': created_inference_job.user.api_keys[0].key})
    assert response.status_code == 200
    inference_job_data = response.get_json()
    assert inference_job_data['id'] == str(created_inference_job.id)
    inference_job_data["name"] = "update_job"
    inference_job_data["job_assignment_type"] = "auto"
    inference_job_data["scaling_type"] = "manual"
    inference_job_data["min_workers"] = 1
    inference_job_data["max_workers"] = 10
    inference_job_data["desired_workers"] = 5
    response = client.put(f'/inference_jobs/{created_inference_job.id}', json=inference_job_data,
                          headers={'X-API-Key': created_inference_job.user.api_keys[0].key})
    assert response.status_code == 200
    inference_job_data = response.get_json()
    assert inference_job_data['name'] == "update_job"
    assert inference_job_data["job_assignment_type"] == "auto"
    assert inference_job_data["scaling_type"] == "manual"
    assert inference_job_data["min_workers"] == 1
    assert inference_job_data["max_workers"] == 10
    assert inference_job_data["desired_workers"] == 5


def test_list_inference_jobs(client, created_inference_job):
    response = client.get('/inference_jobs', headers={'X-API-Key': created_inference_job.user.api_keys[0].key})
    assert response.status_code == 200
    inference_jobs_data = response.get_json()
    assert len(inference_jobs_data) == 1
    assert inference_jobs_data[0]['id'] == str(created_inference_job.id)
    assert inference_jobs_data[0]['name'] == 'Test_Model'


def test_invoke_inference_job_access_denied(client, created_inference_job):
    response = client.post(f'/inference_jobs/{created_inference_job.id}/invoke', json={'input': 'test input'},
                           headers={'X-API-Key': 'invalid-key'})
    assert response.status_code == 403
    data = response.get_json()
    assert data['error'] == 'Invalid API key'


def test_invoke_inference_job_sync_access_denied(client, created_inference_job):
    response = client.post(f'/inference_jobs/{created_inference_job.id}/invoke_sync', json={'input': 'test input'},
                           headers={'X-API-Key': 'invalid-key'})
    assert response.status_code == 403
    data = response.get_json()
    assert data['error'] == 'Invalid API key'


def test_invoke_inference_job_and_invocation(client, created_inference_job):
    invocation_data = {'input': 'test input'}
    response = client.post(f'/inference_jobs/{created_inference_job.id}/invoke', json=invocation_data,
                           headers={'X-API-Key': created_inference_job.user.api_keys[0].key})
    assert response.status_code == 201
    invocation_data = response.get_json()
    assert invocation_data['invocation_id'] is not None
    invocation = Invocation.query.filter_by(id=invocation_data['invocation_id']).first()
    assert invocation.status == 'ENQUEUED'
    assert invocation.input == 'test input'
    assert invocation.result is None
    assert invocation.error is None
    assert invocation.inference_job_id == created_inference_job.id
    invocation.delete_from_db()
    db.session.commit()


def test_create_inference_job_and_set_default_job(client, created_user):
    headers = {'X-API-Key': created_user.api_keys[0].key}
    job_datas = {}
    job_datas['model_id'] = created_user.models[0].id
    job_datas['name'] = created_user.models[0].name
    job_datas['set_as_model_default'] = True
    response = client.post('/inference_jobs', json=job_datas, headers=headers)
    assert response.status_code == 201
    job_id = response.get_json().get('id')

    job = db.session.get(InferenceJob, job_id)
    assert job is not None
    default_inference_job = created_user.models[0].default_inference_job
    assert str(default_inference_job) == job_id
