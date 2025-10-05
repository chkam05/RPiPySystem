from django.shortcuts import render

LINKS = [
    {'name': 'Auth API (Swagger)', 'url': 'http://127.0.0.1:5002/apidocs/'},
    {'name': 'Email API (Swagger)', 'url': 'http://127.0.0.1:5003/apidocs/'},
    {'name': 'Info API (Swagger)', 'url': 'http://127.0.0.1:5004/apidocs/'},
    {'name': 'IO API (Swagger)', 'url': 'http://127.0.0.1:5005/apidocs/'},
]

def links_view(request):
    return render(request, 'links.html', {'links': LINKS})
