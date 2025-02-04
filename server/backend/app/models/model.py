# File: app/models/model.py
from app import db
import uuid
from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import re

DEFAULT_RUN_TIME_IMAGE='nvidia/cuda:11.6.2-runtime-ubuntu20.04'
DEFAULT_INVOKE_FUNCTION='model_invoke.py/invoke'

class Model(db.Model):
    __tablename__ = 'models'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(80), nullable=False)
    model_type = db.Column(db.String(80), nullable=False)
    version = db.Column(db.String(80), nullable=False)
    artifact = db.Column(db.String(80), nullable=False)
    invoke_function = db.Column(db.String(80), default='model_invoke.py/invoke')
    runtime_docker_image = db.Column(db.String(80))
    created_at = db.Column(DateTime(timezone=True), default=func.now())
    updated_at = db.Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    example_input = db.Column(db.String)
    description = db.Column(db.String)
    visibility = db.Column(db.String(80))
    required_gpu = db.Column(db.Integer, default=0)
    default_inference_job = db.Column(UUID(as_uuid=True))

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('models'))  # new relationship

    def __init__(self, name, user_id, model_type, artifact, version, invoke_function=DEFAULT_INVOKE_FUNCTION, runtime_docker_image=DEFAULT_RUN_TIME_IMAGE, example_input="", description="", visibility="private", required_gpu=0, default_inference_job=None):
        self.name = name
        self.user_id = user_id
        self.model_type = model_type
        self.artifact = artifact
        # TODO: support latest as the version. Then fetch from the git to write the SHA
        self.version = version
        self.invoke_function = invoke_function
        self.runtime_docker_image = runtime_docker_image
        self.example_input = example_input
        self.description = description
        self.visibility = visibility
        self.required_gpu = required_gpu
        self.default_inference_job = default_inference_job

    def get(self):
        return self.to_dict()
    
    def get_item_for_list(self):
        return self.to_dict()

    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'name': self.name,
            'user_id': self.user_id,
            'model_type': self.model_type,
            'version': self.version,
            'artifact': self.artifact,
            'invoke_function': self.invoke_function,
            'runtime_docker_image': self.runtime_docker_image,
            'example_input': self.example_input,
            'description': self.description,
            'visibility': self.visibility,
            'required_gpu': self.required_gpu,
            'default_inference_job': self.default_inference_job,
        }

    def _save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def save_db_no_commit(self):
        db.session.add(self)

    def save(self):
        errors = self.validate_values()
        if errors:
            # Raise an exception if there are validation errors
            raise ValueError(f"Validation errors: {', '.join(errors)}") 
        self._save_to_db()

    def delete(self):
        if self.inference_jobs:
            raise ValueError("Cannot delete a model that has inference jobs.")
        self.delete_from_db()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def validate_values(self):
        '''
        Generated with the following prompt:

        Write a validator function:
        
        def validate_values(self):
                # self.name => string with upper, lower, numbers, and _ and -
                # self.model_type => in [text_to_text, text_to_image, text_to_blob]
                # self.artifact => it should be a git repo URL
                # self.version => something as a git SHA
                # self.invoke_function => in a format of file.py/function_name
                # self.runtime_docker_image => in [nvidia/cuda:11.6.2-runtime-ubuntu20.04]
                # self.visibility => in [public, private]
                # self.example_input => string, length less than 1000
                # self.description => string, length less than 1000
                # self.required_gpu => integer, 0 up to 256
        '''

        errors = []

        # Validate self.name
        if not re.match(r"^[a-zA-Z0-9_-]+$", self.name):
            errors.append("Invalid name format.")

        # Validate self.model_type
        valid_model_types = ["text_to_text", "text_to_image", "text_to_blob"]
        if self.model_type not in valid_model_types:
            errors.append(f"Invalid model_type. Expected one of {valid_model_types}.")

        # Validate self.artifact as git repo URL
        if not re.match(r"https?://[^/]+/[^/]+/[^/]+(/)?$", self.artifact):
            errors.append("Invalid artifact format. Expected a git repo URL.")

        # Validate self.version as git SHA
        if not re.match(r"^[a-fA-F0-9]{40}$", self.version):
            errors.append("Invalid version format. Expected a git SHA.")

        # Validate self.invoke_function
        if not re.match(r"^[a-zA-Z0-9_\-]+\.py/[a-zA-Z0-9_\-]+$", self.invoke_function):
            errors.append("Invalid invoke_function format. Expected file.py/function_name format.")

        # Validate self.runtime_docker_image
        valid_docker_images = ["nvidia/cuda:11.6.2-runtime-ubuntu20.04"]
        if self.runtime_docker_image not in valid_docker_images:
            errors.append(f"Invalid runtime_docker_image. Expected one of {valid_docker_images}.")

        # Validate self.visibility
        valid_visibilities = ["public", "private"]
        if self.visibility not in valid_visibilities:
            errors.append(f"Invalid visibility. Expected one of {valid_visibilities}.")

        # Validate self.example_input and self.description
        if len(self.example_input) > 1000:
            errors.append("Example input exceeds 1000 characters.")
        if len(self.description) > 1000:
            errors.append("Description exceeds 1000 characters.")

        # Validate self.required_gpu
        if not isinstance(self.required_gpu, int) or self.required_gpu < 0 or self.required_gpu > 256:
            errors.append("Invalid required_gpu. Expected an integer between 0 and 256.")

        return errors
    
    @classmethod
    def find(cls, id):
        return cls.query.get(id)

    @classmethod
    def find_by_name(cls, user_id, name):
        return cls.query.filter_by(name=name, user_id=user_id).first()
