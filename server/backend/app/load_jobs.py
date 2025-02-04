# File: app/load_jobs.py
from app import app
from app.models.inference_job import InferenceJob
from app.models.invocation import Invocation
from app.models.worker import Worker
from app import db

def load_invocations_to_redis():
    with app.app_context():
        app.r.flushall()
        jobs = InferenceJob.query.all()
        for job in jobs:
            job_id_str = str(job.id)
            invocations = Invocation.query.filter_by(job_id=job.id).filter(Invocation.status != 'COMPLETED').all()
            for invocation in invocations:
                invocation_id_str = str(invocation.id)
                app.r.lpush(f'job:{job_id_str}', invocation_id_str)

def reset_worker_connection_status():
    with app.app_context():
        workers = Worker.query.all()
        for w in workers:
            w.connected = False
            if w.job_assignment_type == "auto":
                w.working_on = None
            db.session.add(w)
        db.session.commit()
