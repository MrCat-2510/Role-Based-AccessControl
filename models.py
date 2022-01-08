from init import db
from flask_login import UserMixin
from sqlalchemy.sql import select, func
from sqlalchemy.orm import backref

# mapping tables
UserRole = db.Table(
    'user_role', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'))
)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    # active = db.Column("is_active",db.Boolean(),nullable=False, server_default='1')
    username = db.Column(db.String(100),nullable=False, unique=True)
    password = db.Column(db.String(100))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    role = db.relationship('Role', secondary=UserRole,lazy='dynamic')
    


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer(), primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer())
    user_name = db.Column(db.String(100))