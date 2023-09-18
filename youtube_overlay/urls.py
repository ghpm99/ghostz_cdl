from django.urls import path
from . import views

urlpatterns = [
    path('auth/', views.get_oauth_token, name='get_oauth_token'),
    path('oauth2callback/', views.oauth2_callback, name='oauth_callback'),
    path('load-playlist/', views.load_playlist, name='load_playlist'),
    path('youtube-playlist/', views.youtube_playlist, name='youtube_playlist'),
]
