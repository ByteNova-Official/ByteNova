# File: app/models/invocation.py
from app import db, app
import uuid
from sqlalchemy import DateTime, func, text
from sqlalchemy.dialects.postgresql import UUID
from app.models.inference_job import InferenceJob
from app.models.worker import Worker

class Invocation(db.Model):
    __tablename__ = 'invocations'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    inference_job_id = db.Column(UUID(as_uuid=True), db.ForeignKey('inference_jobs.id'))
    status = db.Column(db.String(80), default='ENQUEUED')
    processed_by_worker_id = db.Column(UUID(as_uuid=True), db.ForeignKey('workers.id'))
    
    input = db.Column(db.String, default='')
    error = db.Column(db.String)
    result = db.Column(db.String)
    created_at = db.Column(DateTime(timezone=True), default=func.now())  # new created_at field
    updated_at = db.Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())  # new updated_at field
    process_start_time = db.Column(DateTime(timezone=True))
    process_finish_time = db.Column(DateTime(timezone=True))
    processed_by_user = db.Column(UUID(as_uuid=True))
    inference_job_name = db.Column(db.String(80))

    # These relationships can be expensive to query.
    user = db.relationship('User', backref=db.backref('invocations'))
    inference_job = db.relationship('InferenceJob', backref=db.backref('invocations'))
    processed_by_worker = db.relationship('Worker', backref=db.backref('processed_invocations'))

    def get(self):
        item = self.to_dict()
        worker = Worker.query.filter_by(id=self.processed_by_worker_id).first()
        if worker:
            item['processed_by_worker_name'] = worker.name
        if self.process_start_time:
            item['wait_time'] = (self.process_start_time - self.created_at).total_seconds()
        if self.process_finish_time:
            item['process_time'] = (self.process_finish_time - self.process_start_time).total_seconds()
    
    def get_item_for_list(self):
        return self.to_dict()

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'inference_job_id': self.inference_job_id,
            'inference_job_name': self.inference_job_name,
            'status': self.status,
            'processed_by_worker_id': self.processed_by_worker_id,
            'processed_by_worker_name': self.processed_by_worker.name if self.processed_by_worker else '',
            'processed_by_user_id': self.processed_by_user,
            'input': self.input,
            'error': self.error,
            'result': self.result,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'process_start_time': self.process_start_time,
            'process_finish_time': self.process_finish_time,
        }

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
    
    def delete(self):
        self.delete_from_db()

    def __init__(self, inference_job_id, user_id, status=None, input=None, result=None):
        self.inference_job_id = inference_job_id
        self.user_id = user_id
        self.status = status
        self.input = input
        self.result = result
        self.inference_job_name = self.get_inference_job().job_name

    def get_inference_job(self):
        return InferenceJob.query.filter_by(id=self.inference_job_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def save(self):
        self.save_to_db()

    def enqueue(self):
        self.status = 'ENQUEUED'
        app.r.lpush(f'job:{self.inference_job_id}', str(self.id))
        self.save_to_db()

    @classmethod
    def count_user_invocations_last_min(cls, user_id):
        return cls.query.filter_by(user_id=user_id).filter(cls.created_at >= func.now() - text("interval '1 minute'")).count()

    @classmethod
    def find(cls, id):
        return cls.query.get(id)
