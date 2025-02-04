# File: app/routes/login_routes.py

from flask import Blueprint, request, jsonify, current_app
from app.models.user import User

bp = Blueprint('login_routes', __name__)

@bp.route('', methods=['POST'], strict_slashes=False)
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    user = User.find_by_email(email)
    if not user or not user.check_password(password):
        current_app.logger.warning(f'{email} {password} is invalid')
        return jsonify({'error': 'Not authorized'}), 403

    api_key = user.api_keys[0].key if user.api_keys else None
    return jsonify({'api_key': api_key})

