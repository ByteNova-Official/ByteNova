# File: app/routes/api_key_routes.py
from flask import Blueprint, jsonify, app,  current_app
from app.models.api_key import ApiKey
from app.decorators import api_key_required


bp = Blueprint('api_key_routes', __name__)

@bp.route('/', methods=['POST'], strict_slashes=False)
@api_key_required
def create_api_key():
    user_id = app.g.user.id
    new_api_key = ApiKey(user_id)
    new_api_key.save_to_db()
    return jsonify(new_api_key.key), 201

@bp.route('/', methods=['GET'], strict_slashes=False)
@api_key_required
def list_api_keys():
    api_keys = app.g.user.api_keys
    return jsonify([api_key.json() for api_key in api_keys]) 

@bp.route('/<string:key>', methods=['DELETE'], strict_slashes=False)
@api_key_required
def delete_api_key(key):
    api_key = ApiKey.find_by_key(key)
    if not api_key or api_key.user_id != app.g.user.id:
        current_app.logger.warning("You are not authorized to access the resource")
        return jsonify({'error': 'You are not authorized to access the resource.'}), 403

    api_key.delete_from_db()
    return jsonify({'message': 'API Key deleted'})
