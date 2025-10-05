import json, os, secrets, time
from flask import Blueprint, request, jsonify
from ..config import DB_PATH

sessions_bp = Blueprint('auth_sessions', __name__, url_prefix='/api/sessions')

TOKENS = {}

def _load_users():
    with open(DB_PATH) as f:
        return json.load(f)['users']

@sessions_bp.post('')
def login():
    data = request.get_json(force=True)
    users = _load_users()
    for u in users:
        if u['login'] == data['login']:
            import hashlib
            if hashlib.sha256(data['password'].encode()).hexdigest() == u['password']:
                token = secrets.token_hex(16)
                TOKENS[token] = {'login': u['login'], 'exp': time.time() + 3600}
                return jsonify({'token': token})
    return jsonify({'error': 'bad_credentials'}), 401

@sessions_bp.get('')
def me():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    s = TOKENS.get(token)
    if not s or s['exp'] < time.time():
        return jsonify({'error': 'invalid_token'}), 401
    return jsonify({'login': s['login']})
