from flask import Blueprint, request, jsonify

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    HAS_GPIO = True
except Exception:
    HAS_GPIO = False

gpio_bp = Blueprint('io_gpio', __name__, url_prefix='/api/gpio')

@gpio_bp.post('/set')
def set_pin():
    data = request.get_json(force=True)
    pin = int(data['pin'])
    value = int(data['value'])
    if not HAS_GPIO:
        return jsonify({'warning': 'no_gpio_backend'}), 200
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH if value else GPIO.LOW)
    return jsonify({'ok': True})


@gpio_bp.get('/read')
def read_pin():
    pin = request.args.get('pin', type=int)
    if not HAS_GPIO:
        return jsonify({'warning': 'no_gpio_backend', 'value': 0}), 200
    GPIO.setup(pin, GPIO.IN)
    return jsonify({'value': int(GPIO.input(pin))})
