from .service import IOService


if __name__ == '__main__':
    service = IOService()
    service.config()
    service.run()
