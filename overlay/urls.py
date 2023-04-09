from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_overlay, name='get_overlay'),
    path('active/', views.get_active_overlay, name='get_active_overlay'),
    path('import/', views.import_json, name='import_json'),
    path('<int:id>/active', views.update_overlay_active, name='update_overlay_active'),
    path('reload/', views.reload_overlay, name='reload_overlay'),
    path('get-class/', views.get_class_view, name='get_class'),
    path('update-team/', views.update_team, name='update_team'),
]
