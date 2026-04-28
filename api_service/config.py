from typing import Set
import os


# SERVICE CONFIGURATION

HOST = os.getenv('API_SERVICE_HOST')
PORT = int(os.getenv('API_SERVICE_PORT'))
ROUTE = os.getenv('API_SERVICE_ROUTE')
SERVICE_NAME = 'api_service'
SWAGGER_DESCRIPTION = 'RaspberryPi Service API.\n'
SWAGGER_TITLE = 'RaspberryPi Service API'

# AUTHENTICATION

AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL')

# SUPERVISOR

SERVICES_EXCLUDED_FROM_STOP: Set[str] = {'event_listener'} # [eventlistener:event_listener]
SUP_SOC_TIMEOUT = float(os.getenv('SUPERVISOR_SOC_TIMEOUT', '3.0'))
SUP_SOC_URL = os.getenv('SUPERVISOR_SOC_URL')
SUP_SOC_USER = os.getenv('SUPERVISOR_SOC_USER', None)
SUP_SOC_PASS = os.getenv('SUPERVISOR_SOC_PASS', None)