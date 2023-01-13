from django.contrib import admin
from overlay.models import Overlay, Team, Character

# Register your models here.
class OverlayConfig(admin.ModelAdmin):
    list_display = ('id', 'date', 'hour', 'modality', 'active')
    pass

class TeamConfig(admin.ModelAdmin):
    list_display = ('overlay', 'name', 'twitch')
    pass

class CharacterConfig(admin.ModelAdmin):
    list_display = ('family', 'name', 'bdo_class')
    pass

admin.site.register(Overlay, OverlayConfig)
admin.site.register(Team, TeamConfig)
admin.site.register(Character, CharacterConfig)
