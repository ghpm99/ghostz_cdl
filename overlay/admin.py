from django.contrib import admin
from overlay.models import (
    Overlay, Team, Character, BDOClass, ImageBDOClass, User, Background, UserVideo, OverlayType, OverlayReference
)
from authentication.models import AccessToken


# Register your models here.
class OverlayConfig(admin.ModelAdmin):
    list_display = ('id', 'date', 'hour', 'modality', 'active')
    pass


class OverlayTypeConfig(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'default')
    pass


class OverlayReferenceConfig(admin.ModelAdmin):
    list_display = ('id', 'overlay', 'reference')
    pass


class TeamConfig(admin.ModelAdmin):
    list_display = ('id', 'overlay', 'name', 'twitch')
    pass


class CharacterConfig(admin.ModelAdmin):
    list_display = ('id', 'family', 'name', 'bdo_class')
    pass


@admin.display(description='name')
class BDOClassConfig(admin.ModelAdmin):
    ordering = ['name']
    list_display = ('id', 'name', 'json_name')
    pass


class ImageBDOClassConfig(admin.ModelAdmin):
    ordering = ['bdo_class', 'awakening']
    list_display = ('id', 'bdo_class', 'awakening')

    pass


class UserConfig(admin.ModelAdmin):
    ordering = ['family']
    list_display = ('id', 'family')
    pass


class BackgroundConfig(admin.ModelAdmin):
    list_display = ('id', 'type')
    pass


class AccessTokenConfig(admin.ModelAdmin):
    list_display = ('id', 'user')
    pass


class UserVideoConfig(admin.ModelAdmin):
    ordering = ['user']
    list_display = ('id', 'user', 'bdo_class')
    pass


admin.site.register(Overlay, OverlayConfig)
admin.site.register(Team, TeamConfig)
admin.site.register(Character, CharacterConfig)
admin.site.register(BDOClass, BDOClassConfig)
admin.site.register(ImageBDOClass, ImageBDOClassConfig)
admin.site.register(User, UserConfig)
admin.site.register(Background, BackgroundConfig)
admin.site.register(AccessToken, AccessTokenConfig)
admin.site.register(UserVideo, UserVideoConfig)
admin.site.register(OverlayType, OverlayTypeConfig)
admin.site.register(OverlayReference, OverlayReferenceConfig)
