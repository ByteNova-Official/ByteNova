# File: app/auto_scaler.py
from app.models.inference_job import InferenceJob
from app.models.invocation import Invocation
from app import app

def auto_scale(dry_run=False):
    inference_jobs = InferenceJob.query.filter(InferenceJob.desired_workers > InferenceJob.min_workers, InferenceJob.enabled, InferenceJob.scaling_type == 'auto').all()
    scaled_jobs = []
    for inference_job in inference_jobs:
        key = f'invocation_heartbeat_{inference_job.id}'
        waiting_invocation_count = Invocation.query.filter(Invocation.inference_job_id == inference_job.id, Invocation.status == 'ENQUEUED').count()
        if not app.r.get(key) and waiting_invocation_count == 0:
            scaled_jobs.append(inference_job)
            if not dry_run:
                inference_job.scale_down_a_worker()
    if app.debug:
        app.logger.info(f'{len(scaled_jobs)} Jobs that were scaled down: {scaled_jobs}')