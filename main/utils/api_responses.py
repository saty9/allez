from django.http import JsonResponse


def api_failure(reason, verbose_reason=None):
    if not verbose_reason:
        verbose_reason = reason
    return JsonResponse({'success': False,
                         'reason': reason,
                         'verbose_reason': verbose_reason})


def api_success():
    return JsonResponse({'success': True})
