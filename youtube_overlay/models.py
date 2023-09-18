from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class YoutubePlayList(models.Model):
    youtube_id = models.CharField(max_length=40, null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=5000, null=True, blank=True)
    active = models.BooleanField(default=False)


class YoutubeVideo(models.Model):

    STATUS_ENDED = 0
    STATUS_PLAYING = 1
    STATUS_PAUSED = 2
    STATUS_QUEUE = 3

    STATUS = [
        (STATUS_ENDED, 'Finalizado'),
        (STATUS_PLAYING, 'Tocando'),
        (STATUS_PAUSED, 'Pausado'),
        (STATUS_QUEUE, 'Na Fila')
    ]

    status = models.IntegerField(default=STATUS_QUEUE, choices=STATUS)
    youtube_id = models.CharField(max_length=24, null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=5000, null=True, blank=True)
    youtube_playlist = models.ForeignKey(YoutubePlayList, on_delete=models.CASCADE, null=True)


class YoutubeCredentials(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    credentials = models.JSONField(null=True, blank=True)
