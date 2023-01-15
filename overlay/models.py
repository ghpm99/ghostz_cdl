from django.db import models


# Create your models here.
class Overlay(models.Model):
    date = models.TextField()
    hour = models.TextField()
    modality = models.TextField()
    active = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'Id: {self.id} Data: {self.date} Hora: {self.hour}'


class Team(models.Model):
    overlay = models.ForeignKey(Overlay, on_delete=models.CASCADE)
    name = models.TextField()
    twitch = models.TextField()
    mmr = models.TextField()
    mmr_as = models.TextField()

    def __str__(self) -> str:
        return f'Id: {self.id} Name: {self.name}'


class Character(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    family = models.TextField()
    name = models.TextField()
    bdo_class = models.TextField()
    combat_style = models.TextField()
    matches = models.TextField()  # PA
    defeats = models.TextField()  # DE
    victories = models.TextField()  # VI
    champion = models.TextField()  # CA
    dr = models.TextField()  # DR
    by = models.TextField()  # BY
    walkover = models.TextField()  # WO


class BDOClass(models.Model):
    name = models.CharField(max_length=64, unique=True)
    json_name = models.CharField(max_length=64, unique=True)
    video_awakening = models.FileField(upload_to='classvideo/awakening/', null=True)
    video_sucession = models.FileField(upload_to='classvideo/sucession/', null=True)

    def __str__(self):
        return f'{self.name}'

class ImageBDOClass(models.Model):
    bdo_class = models.ForeignKey(BDOClass, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='classimage/')
    awakening = models.BooleanField(default=True)


class User(models.Model):
    family = models.TextField()
    video = models.FileField(upload_to='customvideo/', null=True)