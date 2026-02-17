from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), default='')
    phone = db.Column(db.String(20), default='')
    role = db.Column(db.String(10), default='user')  # 'admin' or 'user'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    grades = db.relationship('Grade', backref='student', lazy=True, cascade='all, delete-orphan')
    documents = db.relationship('Document', backref='owner', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Grade(db.Model):
    __tablename__ = 'grades'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    score = db.Column(db.String(10), nullable=False)
    semester = db.Column(db.String(20), default='')

    def __repr__(self):
        return f'<Grade {self.subject}: {self.score}>'


class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, default=0)
    is_public = db.Column(db.Boolean, default=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(500), default='')

    shared_with = db.relationship('SharedDocument', backref='document', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Document {self.original_name}>'


class SharedDocument(db.Model):
    __tablename__ = 'shared_documents'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    shared_with_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    shared_date = db.Column(db.DateTime, default=datetime.utcnow)

    shared_user = db.relationship('User', foreign_keys=[shared_with_id])

    def __repr__(self):
        return f'<SharedDocument doc={self.document_id} user={self.shared_with_id}>'
