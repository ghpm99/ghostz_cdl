from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_overlay, name='get_overlay'),
    path('import/', views.import_json, name='import_json'),
]
