from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django_celery_results.models import TaskResult


@require_GET
def celery_task_status(request):
    task_id = request.GET.get('task_id')
    if not task_id:
        return JsonResponse({'error': 'no task_id'}, status=400)
    try:
        tr = TaskResult.objects.get(task_id=task_id)
    except TaskResult.DoesNotExist:
        return JsonResponse({'state': 'PENDING'})
    return JsonResponse({
        'state': tr.status,
        'result': tr.result,
    })



