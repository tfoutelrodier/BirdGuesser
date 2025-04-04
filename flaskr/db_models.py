# Holds sqlalchemy ORM based objects
# Just import Base to use this data. It should hold all the information about tables and relationships

from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# association table for a MANY to MANY birds / user_set relationship
# Composite primary key to avoid bird duplicate in a user set
# Use Foreign key to deal with naming and automatic deletion from this table when a bird or a user set is deleted
bird_in_set_table = Table(
    "birds_in_set",
    Base.metadata,
    Column("set_id", Integer, ForeignKey('user_sets.id', ondelete='CASCADE'), nullable=False, primary_key=True),
    Column('bird_id', Integer, ForeignKey('birds.id', ondelete='CASCADE'), nullable=False, primary_key=True)
)


# ORM Objects

class Bird(Base):
    __tablename__ = 'birds'
    id = Column(Integer, primary_key=True, nullable=False)
    gen = Column(String, nullable=False)
    sp = Column(String, nullable=False)
    en = Column(String, nullable=False, unique=True)
    lat = Column(String, nullable=True)
    lng = Column(String, nullable=True)
    url = Column(String, nullable=False)
    file = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    
    # Link to user_sets
    user_sets = relationship(
        "UserSet",
        secondary=bird_in_set_table,
        back_populates="birds"
    )

class UserSet(Base):
    __tablename__ = 'user_sets'
    id = Column(Integer, primary_key=True, autoincrement=True)
    set_name = Column(String, nullable=False, unique=True)
    
    # Link to birds
    birds = relationship(
        "Bird",
        secondary=bird_in_set_table,
        back_populates="user_sets"
    )
