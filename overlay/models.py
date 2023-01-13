from django.db import models

# Create your models here.
class Overlay(models.Model):
    date = models.TextField()
    hour = models.TextField()
    modality = models.TextField()
    active = models.BooleanField(default=False)


class Team(models.Model):
    overlay = models.ForeignKey(Overlay, on_delete=models.CASCADE)
    name = models.TextField()
    twitch = models.TextField()
    mmr = models.TextField()
    mmr_as = models.TextField()

class Character(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    family = models.TextField()
    name = models.TextField()
    bdo_class = models.TextField()
    combat_style = models.TextField()
    matches = models.TextField() #PA
    defeats = models.TextField() #DE
    victories = models.TextField() #VI
    champion = models.TextField() #CA
    dr = models.TextField() #DR
    by  = models.TextField() #BY
    walkover = models.TextField() #WO
