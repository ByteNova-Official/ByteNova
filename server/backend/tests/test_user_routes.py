# File: tests/test_user_routes.py

import pytest
from flask import json
from app import create_app, db
from app.models.user import User
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

    from app.routes import user_routes
    flask_app.register_blueprint(user_routes.bp, url_prefix='/users')
    
    from app.routes import login_routes  # Import the login_routes
    flask_app.register_blueprint(login_routes.bp, url_prefix='/login')

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

def test_create_delete_user(client, user_data):
    response = client.post('/users', json=user_data)
    assert response.status_code == 201
    user_id = response.get_json()

    user = db.session.get(User, user_id)
    assert user is not None
    assert user.name == 'Test User'
    assert user.email == user_data['email']
    assert user.phone == '1234567890'
    assert user.company == 'Test Company'

    headers = {'X-API-Key': user.api_keys[0].key}
    response = client.delete(f'/users/{user_id}', headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'User deleted'
    response = client.get(f'/users/{user_id}', headers=headers)
    assert response.status_code == 403
    user_data = response.get_json()
    assert 'error' in user_data


def test_get_user(client, created_user):
    user_id = created_user.id
    headers = {'X-API-Key': created_user.api_keys[0].key}
    response = client.get(f'/users/{user_id}', headers=headers)
    assert response.status_code == 200
    user_data = response.get_json()
    assert user_data['name'] == 'Test User'
    assert user_data['email'] == created_user.email
    assert user_data['phone'] == '1234567890'
    assert user_data['company'] == 'Test Company'

def test_update_user(client, created_user):
    user_id = created_user.id
    data = {
        'name': 'Updated User',
        'phone': '9876543210'
    }
    headers = {'X-API-Key': created_user.api_keys[0].key}
    response = client.put(f'/users/{user_id}', json=data, headers=headers)
    assert response.status_code == 200
    updated_user_data = response.get_json()
    assert updated_user_data['name'] == 'Updated User'
    assert updated_user_data['phone'] == '9876543210'

def test_delete_user_access_denied(client, created_user):
    user_id = created_user.id
    headers = {'X-API-Key': 'invalid-key'}
    response = client.delete(f'/users/{user_id}', headers=headers)
    assert response.status_code == 403
    data = response.get_json()
    assert data['error'] == 'Invalid API key'

def test_get_user_access_denied(client, created_user):
    user_id = created_user.id
    headers = {'X-API-Key': 'invalid-key'}
    response = client.get(f'/users/{user_id}', headers=headers)
    assert response.status_code == 403
    data = response.get_json()
    assert data['error'] == 'Invalid API key'

def test_update_user_access_denied(client, created_user):
    user_id = created_user.id
    data = {'name': 'Updated User'}
    headers = {'X-API-Key': 'invalid-key'}
    response = client.put(f'/users/{user_id}', json=data, headers=headers)
    assert response.status_code == 403
    data = response.get_json()
    assert data['error'] == 'Invalid API key'

def test_login_positive(client, created_user):
    email = created_user.email
    password = 'password123'
    data = {
        'email': email,
        'password': password
    }
    response = client.post('/login', json=data)
    assert response.status_code == 200
    data = response.get_json()
    assert 'api_key' in data

def test_login_email_not_found(client):
    email = 'nonexistent@example.com'
    password = 'password123'
    data = {
        'email': email,
        'password': password
    }
    response = client.post('/login', json=data)
    assert response.status_code == 403
    data = response.get_json()
    assert data['error'] == 'Not authorized'

def test_login_incorrect_password(client, created_user):
    email = created_user.email
    password = 'incorrectpassword'
    data = {
        'email': email,
        'password': password
    }
    response = client.post('/login', json=data)
    assert response.status_code == 403
    data = response.get_json()
    assert data['error'] == 'Not authorized'
