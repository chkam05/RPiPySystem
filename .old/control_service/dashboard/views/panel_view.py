import requests
from django.shortcuts import render
from django.http import HttpRequest

SUPERVISOR_API = 'http://127.0.0.1:5001/api/processes'

def panel_view(request: HttpRequest):
    try:
        procs = requests.get(SUPERVISOR_API, timeout=5).json()
    except Exception:
        procs = []
    return render(request, 'panel.html', {'processes': procs})
