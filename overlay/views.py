from django.http import JsonResponse
from django.views.decorators.http import require_GET
from ghostz_cdl.decorators import add_cors_react_dev

# Create your views here.
@add_cors_react_dev
@require_GET
def get_ok(request):
    return JsonResponse({'status': 'ok'})