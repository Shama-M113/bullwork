from flask_jwt_extended import verify_jwt_in_request, get_jwt
from functools import wraps
from flask import jsonify

def admin_only(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        if get_jwt()["role"] != "admin":
            return jsonify({"message": "Admin only"}), 403
        return fn(*args, **kwargs)
    return wrapper
