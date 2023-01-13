echo "--> Starting celery process"
celery -A src.tasks beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler