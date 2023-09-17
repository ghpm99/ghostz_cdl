import google_auth_oauthlib.flow
import google.oauth2.credentials
from django.conf import settings
from django.views.decorators.http import require_GET
from django.http import JsonResponse
from django.shortcuts import redirect

import googleapiclient.discovery
import googleapiclient.errors

from ghostz_cdl.decorators import add_cors_react_dev, validate_user
from .models import YoutubeCredentials, YoutubePlayList, YoutubeVideo
from django.contrib.auth.models import User


@add_cors_react_dev
@require_GET
@validate_user
def get_oauth_token(request, user):

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['https://www.googleapis.com/auth/youtube.force-ssl'],
        state=user.id)
    flow.redirect_uri = f'{settings.BASE_URL}/youtube/oauth2callback/'

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

    return JsonResponse({'url': authorization_url})


@add_cors_react_dev
@require_GET
def oauth2_callback(request):

    req = request.GET

    user_id = req.get('state')

    user = User.objects.filter(id=user_id).first()
    if user is None:
        return JsonResponse({'msg': 'User not found'}, status=404)

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['https://www.googleapis.com/auth/youtube.force-ssl'])

    flow.redirect_uri = f'{settings.BASE_URL}/youtube/oauth2callback/'

    authorization_response = request.build_absolute_uri()
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    credentials_json = credentials_to_dict(credentials)
    YoutubeCredentials.objects.update_or_create(
        user=user, defaults={'credentials': credentials_json})

    return redirect(f'{settings.BASE_URL_FRONTEND}/settings/youtube')


def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }


@add_cors_react_dev
@require_GET
@validate_user
def load_playlist(request, user):

    youtube_credentials = YoutubeCredentials.objects.filter(user=user).first()
    if youtube_credentials is None:
        return JsonResponse({'msg': 'Sem credenciais'}, status=400)

    req = request.GET

    playlist_id = req.get('playlist_id')

    if playlist_id is None:
        return JsonResponse({'msg': 'Sem id de playlist'}, status=400)

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
            part="snippet,contentDetails",
            playlistId=item.get('id')
        )
        response_playlist = request_playlist.execute()

        for playlist_item in response_playlist['items']:
            snippet_item = playlist_item['snippet']

            video_title = snippet_item.get('title')
            video_description = snippet_item.get('description')
            resource = snippet_item.get('resourceId')
            video_id = resource.get('videoId')

            YoutubeVideo.objects.update_or_create(
                youtube_id=video_id, youtube_playlist=playlist, defaults={
                    'title': video_title, 'description': video_description}
            )

    return JsonResponse({'msg': 'Playlist carregada com sucesso'})
