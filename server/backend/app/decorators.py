# File: app/decorators.py
import functools

from flask import request, g, jsonify, current_app
from functools import wraps
from app.models.api_key import ApiKey

def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({"error": "API key required"}), 403
        
        api_key_obj = ApiKey.query.filter_by(key=api_key).first()
        if not api_key_obj:
            return jsonify({"error": "Invalid API key"}), 403
        g.user = api_key_obj.user
        try:
            return f(*args, **kwargs)
        except Exception as e:
            current_app.logger.exception(str(e))
            return jsonify({"error": str(e)}), 403

    return decorated_function

# Use only when allowing API requests without AuthN
def api_key_required_with_exception(allowed_ids=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            id = kwargs.get('id', None)
            if not allowed_ids or (id and id not in allowed_ids):
                api_key = request.headers.get('X-API-Key')
                if not api_key:
                    return jsonify({"error": "API key required"}), 403
                
                api_key_obj = ApiKey.query.filter_by(key=api_key).first()
                if not api_key_obj:
                    return jsonify({"error": "Invalid API key"}), 403
                g.user = api_key_obj.user
            try:
                return f(*args, **kwargs)
            except Exception as e:
                current_app.logger.exception(str(e))
                return jsonify({"error": str(e)}), 403
        return decorated_function
    return decorator