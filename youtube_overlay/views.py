import google.oauth2.credentials
import google_auth_oauthlib.flow
from django.shortcuts import redirect
from django.views.decorators.http import require_GET

from ghostz_cdl.decorators import add_cors_react_dev, validate_user

# Create your views here.


@add_cors_react_dev
@require_GET
@validate_user
def get_oauth_token(request, user):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['https://www.googleapis.com/auth/youtube.force-ssl'])
    flow.redirect_uri = 'https://www.example.com/oauth2callback'
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')
    return redirect(authorization_url)
