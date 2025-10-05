import os
from django.core.wsgi import get_wsgi_application

# Ustawienie zmiennej środowiskowej z konfiguracją projektu Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'control_site.settings')

# Tworzymy obiekt aplikacji, który będzie używany przez Gunicorn
application = get_wsgi_application()