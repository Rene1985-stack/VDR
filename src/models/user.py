from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_admin': self.is_admin
        }

class Folder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)

    parent = db.relationship('Folder', remote_side=[id], backref='subfolders')
    creator = db.relationship('User', backref='created_folders')

    def get_path(self):
        """Get the full path of the folder"""
        if self.parent:
            return f"{self.parent.get_path()}/{self.name}"
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id,
            'parent_name': self.parent.name if self.parent else None,
            'path': self.get_path(),
            'created_by': self.created_by,
            'creator_name': self.creator.username if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'description': self.description,
            'subfolder_count': len(self.subfolders),
            'document_count': len(self.documents)
        }

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)
    folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=True)

    uploader = db.relationship('User', backref='uploaded_documents')
    folder = db.relationship('Folder', backref='documents')

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'uploaded_by': self.uploaded_by,
            'uploader_name': self.uploader.username if self.uploader else None,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'description': self.description,
            'folder_id': self.folder_id,
            'folder_name': self.folder.name if self.folder else None,
            'folder_path': self.folder.get_path() if self.folder else None
        }

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    asked_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    asked_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_answered = db.Column(db.Boolean, default=False)

    asker = db.relationship('User', backref='questions')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'asked_by': self.asked_by,
            'asker_name': self.asker.username if self.asker else None,
            'asked_at': self.asked_at.isoformat() if self.asked_at else None,
            'is_answered': self.is_answered,
            'answers': [answer.to_dict() for answer in self.answers]
        }

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    answered_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)

    question = db.relationship('Question', backref='answers')
    answerer = db.relationship('User', backref='answers')

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'question_id': self.question_id,
            'answered_by': self.answered_by,
            'answerer_name': self.answerer.username if self.answerer else None,
            'answered_at': self.answered_at.isoformat() if self.answered_at else None
        }
