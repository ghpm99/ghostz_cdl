from base64 import b64decode
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from authentication.models import AccessToken


def add_cors_react_dev(func):
    def add_cors_react_dev_response(response):

        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = '*'
        response['Access-Control-Allow-Headers'] = 'Authorization, Content-Type, *'

        return response

    def inner(request, *args, **kwargs):
        if request.method == 'OPTIONS':
            return add_cors_react_dev_response(HttpResponse('Ok'))

        result = add_cors_react_dev_response(func(request, *args, **kwargs))
        return result

    return inner


def validate_user(func):
    '''
        `validate_user` is a decorator that blocks users that are not active or staff.

        - It's necessary to pass user `id` and `username` in the header authorization.
        Example: `Authorization: Basic <base64(user_id|username)>`;
        - It's necessary to pass the parameter `user` on the view where this decorator will be called,
        even if this parameter will be not used.
    '''

    def inner(request, *args, **kwargs):
        try:
            user_data = request.META.get('HTTP_AUTHORIZATION')[6:] if request.META.get('HTTP_AUTHORIZATION') else None

            if not user_data:
                return JsonResponse({
                    'msg': 'Empty authorization.'
                }, status=403)

            user_id, username = b64decode(user_data).decode('utf-8').split('|')
            user = User.objects.filter(id=user_id, username=username, is_active=True).first()

            if not user:
                return JsonResponse({'msg': 'User not found.'}, status=401)
        except Exception:
            return JsonResponse({
                'msg': 'Error processing user data.',
                'input': b64decode(user_data).decode('utf-8'),
                'expected_input': 'base64(<user_id>|<username>)',
            }, status=500)

        return func(request, user=user, *args, **kwargs)

    return inner


def validate_super_user(func):
    '''
        `validate_user` is a decorator that blocks users that are not active or staff.

        - It's necessary to pass user `id` and `username` in the header authorization.
        Example: `Authorization: Basic <base64(user_id|username)>`;
        - It's necessary to pass the parameter `user` on the view where this decorator will be called,
        even if this parameter will be not used.
    '''

    def inner(request, *args, **kwargs):
        try:
            user_data = request.META.get('HTTP_AUTHORIZATION')[6:] if request.META.get('HTTP_AUTHORIZATION') else None

            if not user_data:
                return JsonResponse({
                    'msg': 'Empty authorization.'
                }, status=403)

            user_id, username = b64decode(user_data).decode('utf-8').split('|')
            user = User.objects.filter(id=user_id, username=username, is_active=True, is_superuser=True).first()

            if not user:
                return JsonResponse({'msg': 'User not found.'}, status=401)
        except Exception:
            return JsonResponse({
                'msg': 'Error processing user data.',
                'input': b64decode(user_data).decode('utf-8'),
                'expected_input': 'base64(<user_id>|<username>)',
            }, status=500)

        return func(request, user=user, *args, **kwargs)

    return inner


def validate_pusher_user(func):
    def inner(request, *args, **kwargs):
        try:
            user_data = request.META.get('HTTP_AUTHORIZATION')[6:] if request.META.get('HTTP_AUTHORIZATION') else None

            if not user_data:
                return JsonResponse({
                    'msg': 'Empty authorization.'
                }, status=403)

            user = AccessToken.objects.filter(token=user_data).first().user

            if not user:
                return JsonResponse({'msg': 'User not found.'}, status=401)
        except Exception:
            return JsonResponse({
                'msg': 'Error processing user data.',
                'input': user_data,
                'expected_input': 'token',
            }, status=500)

        return func(request, user=user, *args, **kwargs)

    return inner
