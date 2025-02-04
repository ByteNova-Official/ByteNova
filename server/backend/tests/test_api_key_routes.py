# File: tests/test_api_key_routes.py
import pytest
from flask import json
from app import create_app, db
from app.models.user import User
from app.models.api_key import ApiKey
import random
import string


def random_email():
    # Generates a random email address by appending a random string to a base email
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)) + '@example.com'


@pytest.fixture(scope='module')
def client():
    flask_app = create_app('config.TestingConfig')
    from app.routes import api_key_routes
    flask_app.register_blueprint(api_key_routes.bp, url_prefix='/api_keys')

    testing_client = flask_app.test_client()
    with flask_app.app_context():
        db.create_all()
    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()


@pytest.fixture
def api_key(client):
    db.session.begin_nested()

    # Use the random_email function to generate a unique email address for each user
    user_email = random_email()
    user = User(name='Test User', email=user_email, password='test')
    user.save_to_db()
    api_key = ApiKey(user_id=user.id)
    api_key.save_to_db()

    yield api_key.key

    # After the test, delete the created user and api key
    for api_key in user.api_keys:
        api_key.delete_from_db()
    db.session.commit()
    user.delete_from_db()
    db.session.commit()

    db.session.rollback()
    return api_key.key


def test_create_api_key(client, api_key):
    headers = {'X-API-Key': api_key}
    response = client.post('/api_keys', headers=headers)
    assert response.status_code == 201


def test_list_api_keys(client, api_key):
    headers = {'X-API-Key': api_key}
    response = client.get('/api_keys', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)


def test_delete_api_key(client, api_key):
    headers = {'X-API-Key': api_key}
    response = client.delete(f'/api_keys/{api_key}', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'API Key deleted'
    response = client.get('/api_keys', headers=headers)
    assert response.status_code == 403


def test_create_api_key_invalid_api_key(client):
    headers = {'X-API-Key': 'invalid_api_key'}
    response = client.post('/api_keys', headers=headers)
    assert response.status_code == 403
    data = json.loads(response.data)
    assert 'error' in data


def test_delete_api_key_unauthorized(client, api_key):
    headers = {'X-API-Key': api_key}
    # Create a different user with a new API key
    unauthorized_user = User(name='Unauthorized User', email='unauthorized@example.com', password='test')
    unauthorized_user.save_to_db()
    unauthorized_api_key = ApiKey(user_id=unauthorized_user.id)
    unauthorized_api_key.save_to_db()

    response = client.delete(f'/api_keys/{unauthorized_api_key.key}', headers=headers)
    assert response.status_code == 403
    data = json.loads(response.data)
    assert 'error' in data

    # Clean up the unauthorized user and API key
    unauthorized_api_key.delete_from_db()
    unauthorized_user.delete_from_db()
    db.session.commit()


def test_delete_api_key_not_found(client, api_key):
    headers = {'X-API-Key': api_key}
    invalid_key = 'invalid_api_key'

    response = client.delete(f'/api_keys/{invalid_key}', headers=headers)
    assert response.status_code == 403
    data = json.loads(response.data)
    assert 'error' in data
