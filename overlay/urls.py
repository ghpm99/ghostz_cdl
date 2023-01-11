from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_ok, name='get_ok'),
]
