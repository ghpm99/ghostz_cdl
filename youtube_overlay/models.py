from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class YoutubePlayList(models.Model):
    youtube_id = models.CharField(max_length=24, null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)


class YoutubeVideo(models.Model):
    youtube_id = models.CharField(max_length=24, null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)


class YoutubeCredentials(models.Model):
    user = models.ForeignKey(User)
