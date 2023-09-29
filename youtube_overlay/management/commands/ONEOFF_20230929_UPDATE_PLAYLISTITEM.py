import time

import google.oauth2.credentials
import googleapiclient.discovery
import googleapiclient.errors
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from youtube_overlay.models import YoutubeCredentials, YoutubePlayList
from youtube_overlay.views import playlist_item_to_youtube_video


class Command(BaseCommand):
    """
        Update playlist item
    """

    def run_command(self):

        def update_playlist(youtube, playlist_id):
            request_playlists = youtube.playlists().list(
                part="snippet,contentDetails",
                id=playlist_id,
                maxResults=50
            )
            response_playlists = request_playlists.execute()

            for item in response_playlists['items']:
                snippet = item['snippet']

                playlist, created = YoutubePlayList.objects.update_or_create(
                    youtube_id=item.get('id'), defaults={
                        'title': snippet.get('title'), 'description': snippet.get('description')
                    })

                playlist.title = snippet.get('title')
                playlist.description = snippet.get('description')
                playlist.save()

                request_playlist = youtube.playlistItems().list(
                    part="snippet,contentDetails,status",
                    playlistId=item.get('id'),
                    maxResults=50
                )
                response_playlist = request_playlist.execute()

                for playlist_item in response_playlist['items']:
                    playlist_item_to_youtube_video(playlist, playlist_item)

                next_page_token = response_playlist.get('nextPageToken')

                while next_page_token is not None:
                    request_playlist = youtube.playlistItems().list(
                        part="snippet,contentDetails,status",
                        pageToken=next_page_token,
                        playlistId=item.get('id')
                    )
                    response_playlist = request_playlist.execute()

                    for playlist_item in response_playlist['items']:
                        playlist_item_to_youtube_video(playlist, playlist_item)

                    next_page_token = response_playlist.get('nextPageToken')

        user = User.objects.filter(username='ghostz').first()

        youtube_credentials = YoutubeCredentials.objects.filter(user=user).first()
        if youtube_credentials is None:
            print('Sem credenciais')
            return

        api_service_name = "youtube"
        api_version = "v3"
        credentials_dict = youtube_credentials.credentials

        credentials = google.oauth2.credentials.Credentials(
            credentials_dict["token"],
            refresh_token=credentials_dict["refresh_token"],
            token_uri=credentials_dict["token_uri"],
            client_id=credentials_dict["client_id"],
            client_secret=credentials_dict["client_secret"],
            scopes=credentials_dict["scopes"])

        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

        youtube_playlists = YoutubePlayList.objects.all()

        for youtube_playlist in youtube_playlists:
            update_playlist(youtube, youtube_playlist.youtube_id)

    def handle(self, *args, **options):
        begin = time.time()

        self.stdout.write(self.style.SUCCESS('Running...'))

        self.run_command()

        self.stdout.write(self.style.SUCCESS('Success! :)'))
        self.stdout.write(self.style.SUCCESS(
            f'Done with {time.time() - begin}s'))
