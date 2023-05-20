from ..utility import db
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID
from flask_uuid import uuid
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(db.Model):
    __tablename__  = 'users'

    id = db.Column(db.Integer() , primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.Text(), nullable=False)
    url_created = db.relationship('Url' , backref='url_creator' )

    def __repr__(self):
        return f"<user {self.email}>"
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()