import socket, requests
from flask import Blueprint, jsonify

net_bp = Blueprint('info_network', __name__, url_prefix='/api/info')

@net_bp.get('/ip')
def ip_info():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except Exception:
        local_ip = 'unknown'

    try:
        external_ip = requests.get('https://api.ipify.org', timeout=5).text
    except Exception:
        external_ip = 'unknown'
    return jsonify({'local_ip': local_ip, 'external_ip': external_ip})
