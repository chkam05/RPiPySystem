import os

BIND = os.getenv('IO_BIND', '127.0.0.1')
PORT = int(os.getenv('IO_PORT', '5005'))
