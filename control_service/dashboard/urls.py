from django.urls import path
from .views.login_view import login_view
from .views.panel_view import panel_view
from .views.links_view import links_view

urlpatterns = [
    path('', links_view, name='links'),
    path('login/', login_view, name='login'),
    path('panel/', panel_view, name='panel'),
]
