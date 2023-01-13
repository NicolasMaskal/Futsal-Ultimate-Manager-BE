echo "--> Starting beats process"
celery -A src.tasks worker -l info --without-gossip --without-mingle --without-heartbeat