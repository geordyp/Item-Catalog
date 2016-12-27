from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import types

import datetime

Base = declarative_base()

class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
        }


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False)
    description = Column(String(500), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('person.id'), nullable=False)
    user = relationship(Person)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category.name,
            'description': self.description,
        }

engine = create_engine('postgresql://catalog:P1zzaCat@localhost/item_catalog')


Base.metadata.create_all(engine)
