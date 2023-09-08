import google_auth_oauthlib.flow
from django.conf import settings
from django.views.decorators.http import require_GET
from django.http import JsonResponse
from django.shortcuts import redirect

from ghostz_cdl.decorators import add_cors_react_dev, validate_user


@add_cors_react_dev
@require_GET
@validate_user
def get_oauth_token(request, user):

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['https://www.googleapis.com/auth/youtube.force-ssl'])
    flow.redirect_uri = f'{settings.BASE_URL}/youtube/oauth2callback/'

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

    return JsonResponse({'url': authorization_url})


@add_cors_react_dev
@require_GET
def oauth2_callback(request):

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['https://www.googleapis.com/auth/youtube.force-ssl'])

    flow.redirect_uri = f'{settings.BASE_URL}/youtube/oauth2callback/'

    authorization_response = request.build_absolute_uri()
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    session = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    print(session)

    return redirect(f'{settings.BASE_URL_FRONTEND}/settings/youtube')
