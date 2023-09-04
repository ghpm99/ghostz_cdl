from django.urls import path
from . import views

urlpatterns = [
    path('auth', views.get_oauth_token, name='get_oauth_token'),
]
