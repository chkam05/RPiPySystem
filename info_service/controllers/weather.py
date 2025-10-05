from flask import Blueprint, request, jsonify
import requests

weather_bp = Blueprint('info_weather', __name__, url_prefix='/api/weather')

@weather_bp.get('')
def weather():
    lat = request.args.get('lat', type=float, default=52.2297)
    lon = request.args.get('lon', type=float, default=21.0122)
    try:
        r = requests.get(
        'https://api.open-meteo.com/v1/forecast',
        params={'latitude': lat, 'longitude': lon, 'current_weather': True}, timeout=5
        )
        data = r.json()
        return jsonify({'temperature': data.get('current_weather', {}).get('temperature')})
    except Exception:
        return jsonify({'error': 'weather_unavailable'}), 503
