from flask import current_app
from app.models.invocation import Invocation
from app.models.worker import Worker


def inference_job_heartbeat(inference_job):
    key = f'invocation_heartbeat_{inference_job.id}'
    current_app.r.set(key, "invocated", ex=60)


def check_and_scale_inference_job_workers(inference_job):
    if not inference_job.scaling_type == 'auto' or inference_job.desired_workers == inference_job.max_workers:
        return
    detault_ttl = 60
    key = f'autoscaling_inference_job_{inference_job.id}'
    # Try to set the key with a TTL of 60 seconds (1 minute) if it doesn't already exist
    result = current_app.r.set(key, 'wip', ex=detault_ttl, nx=True)
    if result:
        if (inference_job.desired_workers == 0 and inference_job.max_workers > 0) or (
                Invocation.query.filter_by(inference_job_id=inference_job.id, status='ENQUEUED').count() > 1):
            inference_job.desired_workers = 1
        inference_job.save()
        workers = Worker.get_workers_waiting_for_a_job(gpu_limit=inference_job.model_required_gpu)
        if workers:
            w = workers[0]
            w.working_on = inference_job.id
            w.save()
    else:
        # The key already exists, refresh its TTL to 60 seconds
        current_app.r.expire(key, detault_ttl)