
import json
import os

from flask_login import UserMixin
from sqlalchemy import Column, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

connection_str = "sqlite:///"+ os.path.join(BASE_DIR, 'RecipeManagement.db')

Base = declarative_base()

engine = create_engine(connection_str, echo=True)

session = scoped_session(
    sessionmaker(bind=engine)
)

Base.query = session.query_property()


class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    def is_active(self):
        return True

    def get_id(self):
      return str(self.id)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Recipe(Base):
    __tablename__ = 'recipes'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    ingredients = Column(Text)
    instructions = Column(Text)
    created_by = Column(Integer, ForeignKey('users.id'))

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'ingredients': json.loads(self.ingredients),
            'instructions': self.instructions,
            'created_by': self.created_by
        }