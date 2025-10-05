import requests
from django.shortcuts import render, redirect
from django.http import HttpRequest

AUTH_URL = 'http://127.0.0.1:5002/api/sessions'

def login_view(request: HttpRequest):
    if request.method == 'POST':
        login = request.POST.get('login')
        password = request.POST.get('password')
        r = requests.post(AUTH_URL, json={'login': login, 'password': password}, timeout=5)
        if r.status_code == 200:
            request.session['token'] = r.json()['token']
            return redirect('panel')
        return render(request, 'login.html', {'error': 'Błędny login lub hasło'})
    return render(request, 'login.html')
