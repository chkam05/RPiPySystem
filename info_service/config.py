import os

BIND = os.getenv('INFO_BIND', '127.0.0.1')
PORT = int(os.getenv('INFO_PORT', '5004'))
WEATHER_API = os.getenv('WEATHER_API', '')
