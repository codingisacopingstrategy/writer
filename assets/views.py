from django.http import JsonResponse
from django.views.decorators.http import require_GET

from write.local_settings import PUBLIC_PATH

from .listing import DEFAULT_REL, ListingError, assets_root, list_directory


def _forbidden(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'login required'}, status=401)
    if not request.user.has_perm('write.change_mtentry'):
        return JsonResponse({'error': 'not allowed'}, status=403)
    return None


@require_GET
def browse(request):
    denied = _forbidden(request)
    if denied:
        return denied
    rel = request.GET.get('path', DEFAULT_REL)
    query = request.GET.get('q', '')
    try:
        payload = list_directory(assets_root(PUBLIC_PATH), rel, query)
    except ListingError as error:
        return JsonResponse({'error': str(error)}, status=error.status)
    return JsonResponse(payload)
