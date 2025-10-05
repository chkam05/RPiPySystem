from flask import Blueprint, jsonify

health_bp = Blueprint('email_health', __name__, url_prefix='/health')

@health_bp.get('')
def health():
    return jsonify({'status': 'ok'})
