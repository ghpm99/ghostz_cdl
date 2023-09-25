from django.http import JsonResponse
from django.conf import settings
import pusher


pusher_client = pusher.Pusher(
    app_id=settings.ENV_PUSHER_APP_ID,
    key=settings.ENV_PUSHER_KEY,
    secret=settings.ENV_PUSHER_SECRET,
    cluster=settings.ENV_PUSHER_CLUSTER,
    ssl=True
)


def channel_occupied(event):
    if event["channel"] == 'private-overlay':
        pusher_client.trigger('private-events', 'overlay-channel', {'occupied': True})


def channel_vacated(event):
    if event["channel"] == 'private-overlay':
        pusher_client.trigger('private-events', 'overlay-channel', {'occupied': False})


def webhook(request):
    webhook = pusher_client.validate_webhook(
        key=request.headers.get('X-Pusher-Key'),
        signature=request.headers.get('X-Pusher-Signature'),
        body=request.body
    )

    if webhook is None:
        return JsonResponse({'msg': 'Webhook incorreto'}, status=400)

    for event in webhook['events']:
        if event['name'] == "channel_occupied":
            channel_occupied(event)
        elif event['name'] == "channel_vacated":
            channel_vacated(event)

    return JsonResponse({'msg': 'ok'})


def auth(request, channel_name, socket_id):
    auth_response = pusher_client.authenticate(channel=channel_name, socket_id=socket_id)
    return JsonResponse(auth_response)


def send_active_overlay(overlay):
    pusher_client.trigger('private-overlay', 'overlay', {'data': overlay})


def send_overlay_type(type):
    pusher_client.trigger('private-overlay', 'overlay_type', {'data': type})


def send_next_video_youtube(playlist):
    pusher_client.trigger('private-youtube', 'commands', playlist)
