from django.contrib import admin
from youtube_overlay.models import (
    YoutubePlayList, YoutubeVideo
)


# Register your models here.
class YoutubePlayListConfig(admin.ModelAdmin):
    list_display = ('id', 'youtube_id', 'title', 'description', 'active')
    pass


class YoutubeVideoConfig(admin.ModelAdmin):
    list_display = ('id', 'youtube_id', 'status', 'title', 'privacy')
    pass


admin.site.register(YoutubePlayList, YoutubePlayListConfig)
admin.site.register(YoutubeVideo, YoutubeVideoConfig)
