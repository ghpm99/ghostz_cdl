import json

import google_auth_oauthlib.flow
import google.oauth2.credentials
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.http import JsonResponse
from django.shortcuts import redirect
from django.db.models import Count
from lib import pusher

import googleapiclient.discovery
import googleapiclient.errors

from ghostz_cdl.decorators import add_cors_react_dev, validate_user, validate_pusher_user
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

    return JsonResponse({'msg': 'Playlist carregada com sucesso'})


def playlist_item_to_youtube_video(playlist, playlist_item):
    snippet_item = playlist_item['snippet']

    video_title = snippet_item.get('title')
    video_description = snippet_item.get('description')
    resource = snippet_item.get('resourceId')
    video_id = resource.get('videoId')
    position = snippet_item.get('position')

    status = playlist_item['status']
    privacy = status.get('privacyStatus')

    YoutubeVideo.objects.update_or_create(
        position=position, youtube_playlist=playlist, defaults={
            'title': video_title,
            'description': video_description,
            'position': position,
            'privacy': privacy,
            'youtube_id': video_id
        }
    )


@add_cors_react_dev
@require_GET
@validate_user
def get_playlist(request, user):
    youtube_playlist = YoutubePlayList.objects.all().annotate(count_video=Count('youtubevideo'))

    data = [{
        'id': playlist.id,
        'youtube_id': playlist.youtube_id,
        'title': playlist.title,
        'description': playlist.description,
        'active': playlist.active,
        'count': playlist.count_video
    } for playlist in youtube_playlist]

    return JsonResponse({'data': data})


@csrf_exempt
@add_cors_react_dev
@require_POST
@validate_user
def update_active_youtube_playlist(request, user):
    req = json.loads(request.body) if request.body else {}

    playlist_id = req.get('playlist_id')
    youtube_playlist = YoutubePlayList.objects.filter(id=playlist_id).first()
    if youtube_playlist is None:
        return JsonResponse({'msg': 'Playlist não encontrada'}, status=404)

    youtube_playlist.active = True
    youtube_playlist.save()

    active_playlist = YoutubePlayList.objects.filter(active=True).exclude(id=playlist_id).all()
    if active_playlist.__len__() > 0:
        for playlist in active_playlist:
            playlist.active = False
            playlist.save()

    return JsonResponse({'msg': 'ok'})


@add_cors_react_dev
@require_GET
@validate_pusher_user
def get_active_youtube_playlist(request, user):

    active_youtube_videos = YoutubeVideo.objects.filter(
        youtube_playlist__active=True, privacy='public'
    ).exclude(status=YoutubeVideo.STATUS_ENDED).order_by('position')[:2]

    if active_youtube_videos.__len__() < 2:
        YoutubeVideo.objects.filter(youtube_playlist__active=True).update(status=YoutubeVideo.STATUS_QUEUE)
        active_youtube_videos = YoutubeVideo.objects.filter(
            youtube_playlist__active=True, privacy='public'
        ).order_by('position')[:2]

    data = [{
        'id': video.id,
        'youtube_id': video.youtube_id,
        'title': video.title,
        'position': video.position or 0
    } for video in active_youtube_videos]

    return JsonResponse({'data': data})


@add_cors_react_dev
@require_GET
@validate_pusher_user
def next_video_playlist(request, user):

    current_youtube_video = YoutubeVideo.objects.filter(
        youtube_playlist__active=True, status=YoutubeVideo.STATUS_PLAYING, privacy='public'
    ).order_by('position').first()

    if current_youtube_video is not None:
        active_youtube_video = YoutubeVideo.objects.filter(
            youtube_playlist__active=True, position__gt=current_youtube_video.position, privacy='public'
        ).order_by('position').first()
    else:
        active_youtube_video = YoutubeVideo.objects.filter(
            youtube_playlist__active=True, status=YoutubeVideo.STATUS_QUEUE, privacy='public'
        ).order_by('position').first()

    if active_youtube_video is None:
        YoutubeVideo.objects.filter(youtube_playlist__active=True).update(status=YoutubeVideo.STATUS_QUEUE)
        active_youtube_video = YoutubeVideo.objects.filter(
            youtube_playlist__active=True, privacy='public'
        ).order_by('position').first()

    data = {
        'id': active_youtube_video.id,
        'youtube_id': active_youtube_video.youtube_id,
        'title': active_youtube_video.title,
        'position': active_youtube_video.position or 0
    }

    return JsonResponse({'data': data})


@csrf_exempt
@add_cors_react_dev
@require_POST
@validate_pusher_user
def set_state_youtube_video(request, user):
    req = json.loads(request.body) if request.body else {}

    id = req.get('id')
    state = req.get('state')

    if id is None or state is None:
        return JsonResponse({'msg': 'ok'})

    youtube_video = YoutubeVideo.objects.filter(id=id).first()

    if youtube_video is None:
        return JsonResponse({'msg': 'ok'})

    if state == 0:
        youtube_video.status = YoutubeVideo.STATUS_ENDED
        youtube_video.save()
    elif state == 1:
        youtube_video.status = YoutubeVideo.STATUS_PLAYING
        youtube_video.save()
    elif state == 2:
        youtube_video.status = YoutubeVideo.STATUS_PAUSED
        youtube_video.save()

    return JsonResponse({'msg': 'ok'})


@csrf_exempt
@add_cors_react_dev
@require_POST
@validate_user
def skip_video_playlist(request, user):
    current_youtube_video = YoutubeVideo.objects.filter(
        youtube_playlist__active=True, status=YoutubeVideo.STATUS_PLAYING, privacy='public'
    ).all()

    for current in current_youtube_video:
        current.status = YoutubeVideo.STATUS_ENDED
        current.save()

    active_youtube_videos = YoutubeVideo.objects.filter(
        youtube_playlist__active=True, status=YoutubeVideo.STATUS_QUEUE, privacy='public'
    ).order_by('position')[:2]

    if active_youtube_videos.__len__() < 2:
        YoutubeVideo.objects.filter(youtube_playlist__active=True).update(status=YoutubeVideo.STATUS_QUEUE)
        active_youtube_videos = YoutubeVideo.objects.filter(
            youtube_playlist__active=True, privacy='public'
        ).order_by('position')[:2]

    data = [{
        'id': video.id,
        'youtube_id': video.youtube_id,
        'title': video.title,
        'position': video.position or 0
    } for video in active_youtube_videos]

    pusher.send_next_video_youtube(data)
    return JsonResponse({'msg': 'Evento disparado com sucesso'})
