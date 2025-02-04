# File: tests/test_worker_routes.py
import pytest
from flask import json
from app import create_app, db
from app.models.user import User
from app.models.worker import Worker
import random
import string
from tests.test_model_routes import random_email


@pytest.fixture(scope='module')
def client():
    flask_app = create_app('config.TestingConfig')
    from app.routes import user_routes
    flask_app.register_blueprint(user_routes.bp, url_prefix='/users')

    from app.routes import worker_routes
    flask_app.register_blueprint(worker_routes.bp, url_prefix='/workers')

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
def worker_data():
    return {
        'name': 'Test Worker'
    }


@pytest.fixture
def created_worker(client, created_user, worker_data):
    headers = {'X-API-Key': created_user.api_keys[0].key}
    response = client.post('/workers', json=worker_data, headers=headers)
    assert response.status_code == 201
    worker_id = response.get_json().get('id')

    worker = db.session.get(Worker, worker_id)
    assert worker is not None

    yield worker

    # Clean up the created worker
    worker.delete_from_db()
    db.session.commit()


def test_create_delete_worker(client, created_user, worker_data):
    headers = {'X-API-Key': created_user.api_keys[0].key}
    response = client.post('/workers', json=worker_data, headers=headers)
    assert response.status_code == 201
    worker_id = response.get_json().get('id')

    worker = db.session.get(Worker, worker_id)
    assert worker is not None
    assert worker.name == 'Test Worker'

    response = client.delete(f'/workers/{worker_id}', headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Worker deleted'
    response = client.get(f'/workers/{worker_id}', headers=headers)
    assert response.status_code == 403
    worker_data = response.get_json()
    assert 'error' in worker_data


def test_get_worker(client, created_worker):
    worker_id = created_worker.id
    headers = {'X-API-Key': created_worker.user.api_keys[0].key}
    response = client.get(f'/workers/{worker_id}', headers=headers)
    assert response.status_code == 200
    worker_data = response.get_json()
    assert worker_data['name'] == 'Test Worker'
    assert worker_data['user_id'] == str(created_worker.user.id)


def test_list_worker(client, created_worker):
    headers = {'X-API-Key': created_worker.user.api_keys[0].key}
    response = client.get(f'/workers', headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    work_data = data[0]
    print(work_data)
    assert work_data['name'] == 'Test Worker'


def test_update_worker(client, created_worker):
    worker_id = created_worker.id
    headers = {'X-API-Key': created_worker.user.api_keys[0].key}
    update_data = {
        "type": "temp",
        "job_assignment_type": 'auto',
    }
    response = client.put(f'/workers/{worker_id}', headers=headers, json=update_data)
    assert response.status_code == 200
    worker_data = response.get_json()
    assert worker_data['type'] == 'temp'
    assert worker_data['job_assignment_type'] == 'auto'
    worker_id = "test_id"
    response = client.delete(f'/workers/{worker_id}', headers=headers)
    assert response.status_code == 403
    data = response.get_json()
    assert data['error'] == 'You are not authorized to access the resource.'



def test_delete_worker(client, created_worker):
    worker_id = created_worker.id
    headers = {'X-API-Key': created_worker.user.api_keys[0].key}
    response = client.delete(f'/workers/{worker_id}', headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Worker deleted'
    worker_id = "test_id"
    response = client.delete(f'/workers/{worker_id}', headers=headers)
    assert response.status_code == 403
    data = response.get_json()
    assert data['error'] == 'You are not authorized to access the resource.'
