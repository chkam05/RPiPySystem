from .config import HOST, PORT, SECRET
from .service import AuthService


if __name__ == '__main__':
    service = AuthService(HOST, PORT, SECRET)
    service.run()
