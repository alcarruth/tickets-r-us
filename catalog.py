#!/usr/bin/python -i
# -*- coding: utf-8 -*-

import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Date, create_engine, Table, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, backref
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()

#-------------------------------------------------------------------------------------------------
# OPTIONS

# enable exactly one of the following two:
engine_type = 'postgres'
#engine_type = 'sqlite'

db_name = 'catalog'
 
#-------------------------------------------------------------------------------------------------
# Item
# 
class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    price = Column(Integer, nullable=False)
    description = Column(String(250), nullable=False)

    # The current_occupancy solution below works, but I'd like to do the
    # counting on 'the server side' using SQL aggregation and counting,
    # rather than python and len().  I don't know how to do this yet, but
    # this stackoverflow thread looks promising:
    #
    # http://stackoverflow.com/questions/13640298/sqlalchemy-writing-a-hybrid-method-for-child-count
    #
    @hybrid_property
    def current_occupancy(self):
        occupants = filter(lambda p: p.adopters==[], self.puppies)
        return len(occupants)

    def serialize(self):
        return {
            'name': self.name,
            'price': self.price,
            'description': self.description
        }

    def __repr__(self):
        return self.name

#-------------------------------------------------------------------------------------------------
# Category
#
class Category(Base):
    __tablename__ = 'puppy'
    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    items = relationship('Item', secondary='isa', backref=backref('categories'))

    def serialize(self):
        return {
            'name': self.name,
            'items': self.items
        }

    def __repr__(self):
        return self.name

#-------------------------------------------------------------------------------------------------
# Catalog

# Items can be a member of one or more categories and categories
# typically have more than one item.  So this is a many-to-many
# relationship between categories and items.
#
# http://docs.sqlalchemy.org/en/rel_1_0/orm/tutorial.html#building-a-many-to-many-relationship
#
# Table 'catalog' is an association table used to implement
# the many <-> many relationship between adopters and puppies
#
catalog = Table('catalog', Base.metadata,
        Column('item', Integer, ForeignKey('item.id')),
        Column('category', Integer, ForeignKey('category.id')))

#-------------------------------------------------------------------------------------------------
# Users

# think about 
# - authentication
# - authorization

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    # items that user has permission to modify
    items = relationship('Item', backref=backref('users'))

    def serialize(self):
        return {
            'name': self.name,
            'items': self.items
        }

    def __repr__(self):
        return self.name

#-------------------------------------------------------------------------------------------------
# Transactional Functions

def add_user():
    pass

def delete_user():
    pass

def add_item():
    pass

def view_item():
    pass

def edit_item():
    pass

def delete_item():
    pass

#-------------------------------------------------------------------------------------------------

db_urls = {
    'postgres': 'postgresql:///%s' % db_name,
    'sqlite': 'sqlite:///%s.db' % db_name
}
engine = create_engine(db_urls[engine_type])
Base.metadata.create_all(engine)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

# Set the prompt for the python CLI
# - not sure it's really worth doing, but what the heck?
#
def set_prompt(ps):
    sys.ps1 = "\n%s->>> " % ps
    sys.ps2 = " " * len(str(ps)) +  " ... "

# OK, so I'm not using it :-)
# set_prompt(db_name)

# engine_version() returns a string suitable for printing at startup
#
def engine_version():
    if engine_type == 'postgres':
        from psycopg2 import __version__
        return 'psycopg2 (%s)' % __version__
    if engine_type == 'sqlite':
        from sqlite3 import version
        return 'SQLite3 (%s)' % version

# alchemy_version() returns a string suitable for printing at startup
#
def alchemy_version():
    from sqlalchemy import __version__
    return 'SQL Alchemy (%s)' % __version__

startup_info = alchemy_version() + '\n' + str(engine) + '\n'

#-------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    print startup_info

    
