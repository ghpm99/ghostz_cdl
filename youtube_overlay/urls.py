from django.urls import path, include
from . import views

urlpatterns = [
    path('auth/', views.get_oauth_token, name='get_oauth_token'),
    path('oauth2callback/', views.oauth2_callback, name='oauth_callback'),
    path('load-playlist/', views.load_playlist, name='load_playlist'),
    path('playlist/', include([
        path('', views.get_playlist, name='playlist'),
        path('update-active/', views.update_active_youtube_playlist, name='update_active_playlist'),
        path('get-active/', views.get_active_youtube_playlist, name='get_active_playlist'),
        path('set-state/', views.set_state_youtube_video, name='set_state_video'),
    ]))
]
