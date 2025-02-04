#  File: app/models/worker.py
from app import db
import uuid
from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID

class Worker(db.Model):
    __tablename__ = 'workers'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(80))
    status = db.Column(db.String(80))
    connected = db.Column(db.Boolean, default=False)
    working_on = db.Column(UUID(as_uuid=True), db.ForeignKey('inference_jobs.id'))
    info = db.Column(db.String, default='')
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)  # new user_id field
    user = db.relationship('User', backref=db.backref('workers'))  # new relationship
    created_at = db.Column(DateTime(timezone=True), default=func.now())  # new created_at field
    updated_at = db.Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())  # new updated_at field
    available_gpu = db.Column(db.Integer, default=0)  # new available_gpu field
    type = db.Column(db.String(80), default ="longlive")  # temp, longlive
    job_assignment_type = db.Column(db.String(80), default ="manual")  # manual, auto
    recent_deployment_failure = db.Column(db.String)

    def __init__(self, name, user_id, status=None, connected=False, working_on=None, info=None):
        self.name = name
        self.user_id = user_id
        self.status = status
        self.connected = connected
        self.working_on = working_on
        self.info = info

    def _save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def save(self):
        errors = self.validate_values()
        if errors:
            # Raise an exception if there are validation errors
            raise ValueError(f"Validation errors: {', '.join(errors)}") 
        self._save_to_db()

    def refresh(self):
        db.session.refresh(self)

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def delete(self):
        self.delete_from_db()

    def get(self):
        return self.to_dict()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'connected': self.connected,
            'working_on': self.working_on,
            'info': self.info,
            'user_id': self.user_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'available_gpu': self.available_gpu,
            'type': self.type,
            'job_assignment_type': self.job_assignment_type,
            'recent_deployment_failure': self.recent_deployment_failure,
        }

    def validate_values(self):
        errors = []
        # Validate type
        if self.type not in ['temp', 'longlive']:
            errors.append("Invalid type.")
        # Validate job_assignment_type
        if self.job_assignment_type not in ['manual', 'auto']:
            errors.append("Invalid job_assignment_type.")
        return errors

    @classmethod
    def find(cls, id):
        return cls.query.get(id)
    
    @classmethod
    def get_workers_waiting_for_a_job(cls, gpu_limit=None):
        workers = cls.query.filter_by(working_on=None, connected=True, job_assignment_type="auto").all()
        if gpu_limit:
            workers = [worker for worker in workers if worker.available_gpu >= gpu_limit]
        return workers

    @classmethod
    def clean_up_temp_workers(cls):
        temp_workers = cls.query.filter_by(type="temp", connected=False).all()
        for worker in temp_workers:
            worker.delete_from_db()
        print(f'Cleaned up {len(temp_workers)} temp workers.')
