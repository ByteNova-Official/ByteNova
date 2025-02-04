from app import db, app
from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from app.models.model import Model
from app.models.worker import Worker
import uuid
import re

class InferenceJob(db.Model):
    __tablename__ = 'inference_jobs'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_name = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(80), nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(DateTime(timezone=True), default=func.now())
    updated_at = db.Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    model_id = db.Column(UUID(as_uuid=True), db.ForeignKey('models.id'), nullable=False)  # Foreign key to Model
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)  # Foreign key to User
    visibility = db.Column(db.String(80), nullable=True, default='private')
    model_version = db.Column(db.String(80))
    model_invoke_function = db.Column(db.String(80))
    model_example_input = db.Column(db.String)
    description = db.Column(db.String)
    min_workers = db.Column(db.Integer)
    max_workers = db.Column(db.Integer)
    desired_workers = db.Column(db.Integer)
    model_required_gpu = db.Column(db.Integer)
    job_assignment_type = db.Column(db.String(80), default ="manual")  # manual, auto
    scaling_type = db.Column(db.String(80), default ="auto")  # auto, manual

    # Relationships
    model = db.relationship('Model', backref=db.backref('inference_jobs'))
    user = db.relationship('User', backref=db.backref('inference_jobs'))

    def __init__(self, name, model_id, user_id, enabled=True, status='verified', visibility="private", description="", min_workers=1, max_workers=1, desired_workers=1, job_assignment_type="manual", scaling_type="auto"):
        self.job_name = name    # up to 80 characters, string with upper, lower, numbers, and _ and -, if  visiblility is public, this has to be globally unique
        self.model_id = model_id    # Foreign key to Model
        self.user_id = user_id      # Foreign key to User
        self.enabled = enabled # True, False
        self.status = status  # verified, unverified, verification_failed
        self.visibility = visibility # private, public
        self.description = description # up to 1000 characters
        self.min_workers = min_workers # 0-1000
        self.max_workers = max_workers # 0-1000, > desired_workers
        self.desired_workers = desired_workers # 0-1000, > min_workers
        self.job_assignment_type = job_assignment_type # manual, auto
        self.scaling_type = scaling_type # auto, manual

    def sync_info_from_model(self):
        model = self.get_model()
        self.model_version = model.version
        self.model_invoke_function = model.invoke_function
        self.model_example_input = model.example_input
        self.model_required_gpu = model.required_gpu
        if self.description == "":
            self.description = model.description
        self.save()

    def _save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def save(self):
        errors = self.validate_values()
        if errors:
            # Raise an exception if there are validation errors
            raise ValueError(f"Validation errors: {', '.join(errors)}") 
        self._save_to_db()

    def delete(self):
        workers = Worker.query.filter_by(working_on=self.id).all()
        for worker in workers:
            worker.working_on = None
            worker.save()
        self.delete_from_db()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
    
    def get_model(self):
        return Model.query.filter_by(id=self.model_id).first()
    
    def get_activate_worker_count(self):
        return Worker.query.filter_by(working_on=self.id, connected=True).count()
    
    def get_serving_worker_count(self):
        return Worker.query.filter_by(working_on=self.id, connected=True, status='SERVING').count()

    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'name': self.job_name,
            'status': self.status,
            'enabled': self.enabled,
            'user_id': self.user_id,
            'visibility': self.visibility,
            'description': self.description,
            'min_workers': self.min_workers,
            'max_workers': self.max_workers,
            'desired_workers': self.desired_workers,
            'job_assignment_type': self.job_assignment_type,
            'scaling_type': self.scaling_type,
        }

    def get(self):
        item = self.to_dict()
        item['active_workers'] = self.get_activate_worker_count()
        item['model_id'] = self.model_id
        item['model_name'] = self.get_model().name
        item['model_artifact'] = self.get_model().artifact
        item['model_version'] = self.model_version
        item['model_example_input'] = self.model_example_input
        item['model_required_gpu'] = self.model_required_gpu
        return item
    
    def get_item_for_list(self):
        # return self.to_dict()
        return self.get()        

    def scale_down_a_worker(self):
        if self.desired_workers > self.min_workers:
            self.desired_workers -= 1
            self.save()
            worker = Worker.query.filter_by(working_on=self.id, connected=True, job_assignment_type='auto').first()
            if worker:
                worker.working_on = None
                worker.status = "IDLE"
                worker.save()
                return worker
        return None

    def validate_values(self):
        errors = []
        # Validate job_name
        if not re.match("^[a-zA-Z0-9_-]{1,80}$", self.job_name):
            errors.append("Invalid job name format.")
        # Additional check for global uniqueness if visibility is public needs to be done externally.
        # Validate enabled
        if not isinstance(self.enabled, bool):
            errors.append("Invalid enabled value. Should be a boolean.")
        # Validate status
        if self.status not in ['verified', 'unverified', 'verification_failed']:
            errors.append("Invalid status value.")
        # Validate visibility
        if self.visibility not in ['private', 'public']:
            errors.append("Invalid visibility value.")
        # Validate description
        if len(self.description) > 1000:
            errors.append("Description too long.")
        # Validate min_workers, max_workers, and desired_workers
        if not (0 <= self.min_workers <= 1000 and 0 <= self.max_workers <= 1000 and 0 <= self.desired_workers <= 1000):
            errors.append("Invalid worker count. Should be between 0 and 1000.")
        if not (self.max_workers >= self.desired_workers and self.desired_workers >= self.min_workers):
            errors.append("Invalid worker relationship. Should be min_workers <= desired_workers <= max_workers.")
        # Validate job_assignment_type
        if self.job_assignment_type not in ['manual', 'auto']:
            errors.append("Invalid job_assignment_type.")
        if self.scaling_type not in ['manual', 'auto']:
            errors.append("Invalid scaling_type.")
        return errors

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find(cls, id):
        return cls.query.get(id)

    @classmethod
    def get_jobs_to_match(cls):
        return cls.query.filter_by(enabled=True, job_assignment_type="auto").all()