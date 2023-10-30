import time
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from youtube_overlay.models import YoutubePlayList
from overlay.models import Overlay


class Command(BaseCommand):
    """
        Set Ghostz user for all databases
    """

    def run_command(self):
        user = User.objects.filter(username='ghostz').first()

        playlists = YoutubePlayList.objects.all()
        for playlist in playlists:
            playlist.user = user
            playlist.save()

        overlay_list = Overlay.objects.all()
        for overlay in overlay_list:
            overlay.user = user
            overlay.save()

    def handle(self, *args, **options):
        begin = time.time()

        self.stdout.write(self.style.SUCCESS('Running...'))

        self.run_command()

        self.stdout.write(self.style.SUCCESS('Success! :)'))
        self.stdout.write(self.style.SUCCESS(
            f'Done with {time.time() - begin}s'))
