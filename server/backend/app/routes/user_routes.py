# File: app/routes/user_routes.py
import os
from flask import Blueprint, request, jsonify, app, render_template, current_app
from werkzeug.security import generate_password_hash
from app.models.user import User
from app.models.api_key import ApiKey
from app.decorators import api_key_required
from datetime import datetime
from app.utils import send_verification_email
from app.utils import is_valid_uuid

bp = Blueprint('user_routes', __name__)

def check_resource_ownership(id):
    if not is_valid_uuid(id):
        return None
    user = User.query.filter_by(id=id).first()
    if user and user.id == app.g.user.id:
        return user
    return None

@bp.route('/', methods=['POST'], strict_slashes=False)
def create_user():
    name = request.json.get('name')
    email = request.json.get('email')
    password = request.json.get('password')  # Get password from request
    phone = request.json.get('phone')
    company = request.json.get('company')
    if User.find_by_email(email):
        current_app.logger.warning(f"{email} User already exists")
        return jsonify({'error': 'User already exists'}), 403

    new_user = User(name, email, password, phone, company)
    new_user.save_to_db()

    # Create an API key for the new user
    new_api_key = ApiKey(user_id=new_user.id)
    new_api_key.save_to_db()
    if os.getenv('FLASK_ENV') == 'production':
        current_app.logger.info(f"start send verify email for {new_user.email}")
        send_verification_email(f'https://console.clustro.ai/api/users/verify/{new_user.id}', new_user.email)

    return jsonify(new_user.id), 201

@bp.route('/', methods=['GET'], strict_slashes=False)
@api_key_required
def get_single_user():
    return jsonify(app.g.user.json())

@bp.route('/<string:id>', methods=['GET'], strict_slashes=False)
@api_key_required
def get_user(id):
    user = check_resource_ownership(id)
    if not user:
        current_app.logger.warning("get_user You are not authorized to access the resource")
        return jsonify({'error': 'You are not authorized to access the resource.'}), 403
    return jsonify(user.json())

@bp.route('/<string:id>', methods=['PUT'], strict_slashes=False)
@api_key_required
def update_user(id):
    user = check_resource_ownership(id)
    if not user:
        current_app.logger.warning("update_user You are not authorized to access the resource")
        return jsonify({'error': 'You are not authorized to access the resource.'}), 403
    
    data = request.get_json()
    if 'name' in data:
        user.name = data['name']
    if 'email' in data:
        user.email = data['email']
    if 'phone' in data:
        user.phone = data['phone']
    if 'company' in data:
        user.company = data['company']
    user.save_to_db()
    return jsonify(user.json())

@bp.route('/<string:id>', methods=['DELETE'], strict_slashes=False)
@api_key_required
def delete_user(id):
    user = check_resource_ownership(id)
    if not user:
        current_app.logger.warning("delete_user You are not authorized to access the resource")
        return jsonify({'error': 'You are not authorized to access the resource.'}), 403
    
    user.delete_from_db()
    return jsonify({'message': 'User deleted'})

@bp.route('/verify/<string:id>', methods=['GET'], strict_slashes=False)
def verify_user(id):
    user = User.query.filter_by(id=id).first()
    if not user:
        current_app.logger.warning("verify_user You are not authorized to access the resource")
        return jsonify({'error': 'You are not authorized to access the resource.'}), 403
    if not user.verified_at:
        user.verified_at = datetime.utcnow()
        user.save_to_db()
    return render_template('email_verify.html')
