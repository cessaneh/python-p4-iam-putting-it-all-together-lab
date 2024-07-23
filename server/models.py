from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from flask_bcrypt import Bcrypt
from sqlalchemy_serializer import SerializerMixin
from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    _password_hash = Column(String(128), nullable=False)
    image_url = Column(String(255))
    bio = Column(String(500))
    
    
    recipes = relationship('Recipe', back_populates='user', lazy=True)

    @property
    def password(self):
        raise AttributeError("Password is not readable")

    @password.setter
    def password(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'image_url': self.image_url,
            'bio': self.bio
        }

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    instructions = Column(String(500), nullable=False)
    minutes_to_complete = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    
    user = relationship('User', back_populates='recipes')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'instructions': self.instructions,
            'minutes_to_complete': self.minutes_to_complete,
            'user': self.user.to_dict() if self.user else None
        }
