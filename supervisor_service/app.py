from supervisor_service.service import SupervisorService


if __name__ == '__main__':
    service = SupervisorService()
    service.run()