# File: app/routes/invocation_routes.py
from flask import Blueprint, jsonify, g, current_app
from app.models.invocation import Invocation
from app.decorators import api_key_required
from app.utils import is_valid_uuid

bp = Blueprint('invocation_routes', __name__)

def check_resource_ownership(id):
    if not is_valid_uuid(id):
        return None
    invocation = Invocation.query.filter_by(id=id).first()
    if invocation and invocation.user_id == g.user.id:
        return invocation
    return None

@bp.route('/', methods=['GET'], strict_slashes=False)
@api_key_required
def get_invocations():
    invocations = g.user.invocations
    return jsonify([invocation.to_dict() for invocation in invocations][::-1]) 

@bp.route('/<string:id>', methods=['GET'], strict_slashes=False)
@api_key_required
def get_invocation(id):
    invocation = check_resource_ownership(id)
    if not invocation:
        current_app.logger.warning('You are not authorized to access the resource.')
        return jsonify({'error': 'You are not authorized to access the resource.'}), 403
    
    return jsonify(invocation.to_dict())
