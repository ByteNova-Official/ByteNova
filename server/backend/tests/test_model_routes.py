# File: tests/test_model_routes.py
import redis
import pytest
from flask import json
from app import create_app, db
from app.models.user import User
from app.models.model import Model
from app.models.invocation import Invocation
import random
import string


def random_email():
    # Generates a random email address by appending a random string to a base email
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)) + '@example.com'


@pytest.fixture(scope='module')
def client():
    flask_app = create_app('config.TestingConfig')
    flask_app.r = redis.Redis(host=flask_app.config['REDIS_HOST'], port=6379, db=0)
    from app.routes import api_key_routes
    flask_app.register_blueprint(api_key_routes.bp, url_prefix='/api_keys')

    from app.routes import user_routes
    flask_app.register_blueprint(user_routes.bp, url_prefix='/users')

    from app.routes import model_routes  # Import the model_routes
    flask_app.register_blueprint(model_routes.bp, url_prefix='/models')

    from app.routes import inference_job_routes
    flask_app.register_blueprint(inference_job_routes.bp, url_prefix='/inference_jobs')

    testing_client = flask_app.test_client()
    with flask_app.app_context():
        db.create_all()
    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()


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

    user = db.session.get(User, user_id)
    assert user is not None

    yield user

    # Clean up the created user
    user.delete_from_db()
    db.session.commit()


@pytest.fixture
def model_data():
    return {
        "name": "Test_Model",
        "model_type": "text_to_text",
        "version": "7a3e7912c114cec6e833a7afb9a77304b1402926",
        "artifact": "https://github.com/ClustroAI/dummy_model_1_llm",
        "invoke_function": "model_invoke.py/invoke"
    }


@pytest.fixture
def created_model(client, created_user, model_data):
    headers = {'X-API-Key': created_user.api_keys[0].key}
    response = client.post('/models', json=model_data, headers=headers)
    assert response.status_code == 201
    model_id = response.get_json().get('id')

    model = db.session.get(Model, model_id)
    assert model is not None

    yield model

    # Clean up the created model
    model.delete_from_db()
    db.session.commit()


@pytest.fixture
def created_model_default_job(client, created_user, model_data):
    headers = {'X-API-Key': created_user.api_keys[0].key}
    response = client.post('/models', json=model_data, headers=headers)
    assert response.status_code == 201
    model_id = response.get_json().get('id')

    model = db.session.get(Model, model_id)
    assert model is not None
    job_data = {}
    job_data['model_id'] = created_user.models[0].id
    job_data['name'] = created_user.models[0].name
    job_data['set_as_model_default'] = True
    response = client.post('/inference_jobs', json=job_data, headers=headers)
    assert response.status_code == 201
    job_id = response.get_json().get('id')
    db.session.refresh(model)
    model = db.session.get(Model, model_id)
    default_inference_job = model.default_inference_job
    assert str(default_inference_job) == job_id

    yield model

    # Clean up the created model
    response = client.delete(f'/inference_jobs/{job_id}', headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Inference Job deleted'
    model.delete_from_db()
    db.session.commit()


@pytest.fixture
def created_model_default_job_no_delete(client, created_user, model_data):
    headers = {'X-API-Key': created_user.api_keys[0].key}
    response = client.post('/models', json=model_data, headers=headers)
    assert response.status_code == 201
    model_id = response.get_json().get('id')

    model = db.session.get(Model, model_id)
    assert model is not None
    job_data = {}
    job_data['model_id'] = created_user.models[0].id
    job_data['name'] = created_user.models[0].name
    job_data['set_as_model_default'] = True
    response = client.post('/inference_jobs', json=job_data, headers=headers)
    assert response.status_code == 201
    job_id = response.get_json().get('id')
    db.session.refresh(model)
    model = db.session.get(Model, model_id)
    default_inference_job = model.default_inference_job
    assert str(default_inference_job) == job_id

    yield model

    # Clean up the created model
    model.delete_from_db()
    db.session.commit()


def test_create_delete_model(client, created_user, model_data):
    headers = {'X-API-Key': created_user.api_keys[0].key}
    response = client.post('/models', json=model_data, headers=headers)
    assert response.status_code == 201
    model_id = response.get_json().get('id')
    model = db.session.get(Model, model_id)
    assert model is not None
    assert model.name == 'Test_Model'
    assert model.model_type == 'text_to_text'
    assert model.version == '7a3e7912c114cec6e833a7afb9a77304b1402926'
    assert model.artifact == 'https://github.com/ClustroAI/dummy_model_1_llm'
    assert model.invoke_function == 'model_invoke.py/invoke'

    response = client.delete(f'/models/{model_id}', headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Model deleted'
    response = client.get(f'/models/{model_id}', headers=headers)
    assert response.status_code == 403
    data = response.get_json()
    assert 'error' in data


def test_get_model(client, created_model):
    model_id = created_model.id
    headers = {'X-API-Key': created_model.user.api_keys[0].key}
    response = client.get(f'/models/{model_id}', headers=headers)
    assert response.status_code == 200
    model_data = response.get_json()
    assert model_data['name'] == 'Test_Model'
    assert model_data['model_type'] == 'text_to_text'
    assert model_data['version'] == '7a3e7912c114cec6e833a7afb9a77304b1402926'
    assert model_data['artifact'] == 'https://github.com/ClustroAI/dummy_model_1_llm'
    assert model_data['invoke_function'] == 'model_invoke.py/invoke'


def test_update_model(client, created_model):
    model_id = created_model.id
    headers = {'X-API-Key': created_model.user.api_keys[0].key}
    response = client.get(f'/models/{model_id}', headers=headers)
    assert response.status_code == 200
    model_data = response.get_json()
    assert model_data['name'] == 'Test_Model'
    model_data["required_gpu"] = 100
    response = client.put(f'/models/{model_id}', headers=headers, json=model_data)
    assert response.status_code == 200
    model_data = response.get_json()
    assert model_data['required_gpu'] == 100


def test_list_models(client, created_model):
    headers = {'X-API-Key': created_model.user.api_keys[0].key}
    response = client.get('/models', headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    model_data = data[0]
    assert model_data['name'] == 'Test_Model'
    assert model_data['model_type'] == 'text_to_text'
    assert model_data['version'] == '7a3e7912c114cec6e833a7afb9a77304b1402926'
    assert model_data['artifact'] == 'https://github.com/ClustroAI/dummy_model_1_llm'
    assert model_data['invoke_function'] == 'model_invoke.py/invoke'


def test_delete_model_access_denied(client, created_model):
    model_id = created_model.id
    headers = {'X-API-Key': 'invalid-key'}
    response = client.delete(f'/models/{model_id}', headers=headers)
    assert response.status_code == 403
    data = response.get_json()
    assert data['error'] == 'Invalid API key'


def test_get_model_access_denied(client, created_model):
    model_id = created_model.id
    headers = {'X-API-Key': 'invalid-key'}
    response = client.get(f'/models/{model_id}', headers=headers)
    assert response.status_code == 403
    data = response.get_json()
    assert data['error'] == 'Invalid API key'


def test_model_invoke_with_no_default_inference_job(client, created_model):
    model_id = created_model.id
    invocation_data = {'input': 'test input'}
    response = client.post(f'/models/{model_id}/invoke', json=invocation_data,
                           headers={'X-API-Key': created_model.user.api_keys[0].key})

    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == 'model miss default_inference_job'


def test_model_invoke(client, created_model_default_job):
    model_id = created_model_default_job.id
    invocation_data = {'input': 'test input'}
    response = client.post(f'/models/{model_id}/invoke', json=invocation_data,
                           headers={'X-API-Key': created_model_default_job.user.api_keys[0].key})
    assert response.status_code == 201
    invocation_data = response.get_json()
    assert invocation_data['invocation_id'] is not None
    invocation = Invocation.query.filter_by(id=invocation_data['invocation_id']).first()

    assert invocation.status == 'ENQUEUED'
    assert invocation.input == 'test input'
    assert invocation.result is None
    assert invocation.error is None
    assert invocation.inference_job_id == created_model_default_job.default_inference_job
    invocation.delete_from_db()
    db.session.commit()


def test_model_invoke_delete_job(client, created_model_default_job_no_delete):
    model_id = created_model_default_job_no_delete.id
    invocation_data = {'input': 'test input'}
    job_id = str(created_model_default_job_no_delete.default_inference_job)
    headers = {'X-API-Key': created_model_default_job_no_delete.user.api_keys[0].key}
    response = client.delete(f'/inference_jobs/{job_id}', headers=headers)
    print(response.get_json())
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Inference Job deleted'

    response = client.post(f'/models/{model_id}/invoke', json=invocation_data,
                           headers={'X-API-Key': created_model_default_job_no_delete.user.api_keys[0].key})

    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == 'default inference job not found'
