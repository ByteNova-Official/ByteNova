# File: app/models/user.py
from app import db
import uuid
from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    company = db.Column(db.String(80), nullable=True)
    password_hash = db.Column(db.String(128))  # New password field
    created_at = db.Column(DateTime(timezone=True), default=func.now())  # new created_at field
    updated_at = db.Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())  # new updated_at field
    verified_at = db.Column(DateTime(timezone=True), nullable=True)

    def __init__(self, name, email, password, phone=None, company=None):
        self.name = name
        self.email = email
        self.phone = phone
        self.company = company
        self.password_hash = generate_password_hash(password)  # Hashing the password

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)  # Check if the password matches

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'company': self.company,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'verified_at': self.verified_at,
        }

    def delete_all_resources(self):
        for api_key in self.api_keys:
            api_key.delete_from_db()
        for worker in self.workers:
            worker.delete_from_db()
        for inference_job in self.inference_jobs:
            inference_job.delete_from_db()
        for model in self.models:
            model.delete_from_db()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def save(self):
        self.save_to_db()

    def delete_from_db(self):
        self.delete_all_resources()
        db.session.delete(self)
        db.session.commit()

    def delete(self):
        self.delete_from_db()

    @classmethod
    def find(cls, id):
        return cls.query.get(id)

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.get(_id)

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
