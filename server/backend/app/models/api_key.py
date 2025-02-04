# File: app/models/api_key.py
import secrets
from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import UUID

class ApiKey(db.Model):
    __tablename__ = 'api_keys'

    key = db.Column(db.String(80), primary_key=True, unique=True, default=lambda: 'sk-' + secrets.token_urlsafe(50))
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('api_keys'))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, user_id):
        self.user_id = user_id

    @classmethod
    def find_by_key(cls, key):
        return cls.query.filter_by(key=key).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def save(self):
        self.save_to_db()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def json(self):
        return {
            'key': self.key,
            'user_id': self.user_id,
            'created_at': self.created_at
        }
