from django.contrib import admin
from overlay.models import Overlay, Team, Character, BDOClass, ImageBDOClass, User


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


@admin.display(description='name')
class BDOClassConfig(admin.ModelAdmin):
    list_display = ('id', 'name', 'json_name')
    pass


class ImageBDOClassConfig(admin.ModelAdmin):
    list_display = ('id', 'bdo_class')
    pass


class UserConfig(admin.ModelAdmin):
    list_display = ('id', 'family')
    pass


admin.site.register(Overlay, OverlayConfig)
admin.site.register(Team, TeamConfig)
admin.site.register(Character, CharacterConfig)
admin.site.register(BDOClass, BDOClassConfig)
admin.site.register(ImageBDOClass, ImageBDOClassConfig)
admin.site.register(User, UserConfig)
