#!/usr/bin/python -i
# -*- coding: utf-8 -*-

import json
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, backref
from sqlalchemy.ext.hybrid import hybrid_property

#---------
# OPTIONS
#---------

engine_type = 'postgres'
#engine_type = 'sqlite'

db_name = 'tickets'

Base = declarative_base()

#---------------------------------------------------------------
# Conference - a collection of Teams
# 
class Conference(Base):
    __tablename__ = 'conference'
   
    abbrev_name = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    logo = Column(String, nullable=False)
    teams = relationship('Team')

    def __repr__(self):
        return self.name
 

#---------------------------------------------------------------
# Teams

class Team(Base):
    __tablename__ = 'team'

    id = Column(Integer, primary_key = True)
    name =Column(String, nullable = False)
    nickname = Column(String)
    espn_id =  Column(Integer)
    city =  Column(String)
    state = Column(String)
    conference = Column(String, ForeignKey('conference.abbrev_name'))
    logo = Column(String)
    
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'nickname': self.nickname,
            'espn_id': self.espn_id,
            'city': self.city,
            'state': self.state,
            #'conference': self.conference
        }

    def __repr__(self):
        return self.name

#---------------------------------------------------------------
# Games - a pairing of Teams
# - the venue is the stadium of the home team
#
# TODO: generalize Game to 'Event'
# - add field for event_type, e.g. 'football_game', 'concert'
# - maybe Football_Game is a subclass of Event?
#   home_team and visiting_team make no sense for general Event
# 
class Game(Base):
    __tablename__ = 'game'
   
    id = Column(Integer, primary_key=True)
    home_team = Column(String, nullable=False)
    visiting_team = Column(String, nullable=False)
    tickets = relationship('Ticket')
    
    def __repr__(self):
        return self.name

 
#---------------------------------------------------------------
# Seller - someone with a ticket they're trying to sell

class Seller(Base):
    __tablename__ = 'seller'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    tickets = relationship('Ticket')


#---------------------------------------------------------------
# Tickets - a seat at a Game
#
# TODO: We have in effect two references to the venue:
#  - ticket.game.home_team
#  - ticket.seat.venue
# These must be identical (or should they? games are
# sometimes played at neutral sites.

class Ticket(Base):
    __tablename__ = 'ticket'

    id = Column(Integer, primary_key=True)
    game = Column(Integer, ForeignKey('game.id'))
    seat = Column(Integer, ForeignKey('seat.id'))
    UniqueConstraint('game', 'seat')
    seller = Column(Integer, ForeignKey('seller.id'))

    def serialize(self):
        return {
            'game': self.game,
            'seat': self.seat
        }

    def __repr__(self):
        return self.name

#---------------------------------------------------------------
# Seat
#
# Question: Do I really need this table?  It would be large.
# 80,000 seats at 100 different stadiums.  Maybe just
# a data structure specifying the stadium layout.
# or a table of seat __rows__.  Or each section is just a
# dict mapping row number to number of seats in the row, 
# or (start, end) pair so the seat numbers might be generated
# by range(start, end).
#
# Answer: Yes, I really need this table.  It doesn't have to
# be any larger than the number of tickets in the database.
# Some spec as in the paragraph above will serve as a constraint
# on the data entered into the table.
#
# - a seat is a unique physical spot at a stadium
# - the venue is here a reference to the home team, 
#   so the only venues we have are team's stadiums.
#
# TODO: implement venues other than home stadiums.
# - add a Stadium class
# - add a home_field column for each team refering to their stadium
# - allow *-1 teams to stadium, teams can share a home field.
#   (like the NY Jets and NY Giants do, for example)
#
# Table Seat should be populated in the init code for this project
# and should contain all the seats for all the teams' stadiums.

# TODO: multi-column primary key as foreign key
# Table Ticket refers to table Seat's primary key.  There is some
# issue in doing this with a 'multi-column' primary key, which I
# have decide to use here since (section, row, number) uniquely
# identifies a seat.  I think what I can do is just use an Integer 
# id and then require that (section, row, number) be unique.
# Checking SQLAlchemy docs ...

class Seat(Base):
    __tablename__ = 'seat'

    id = Column(Integer, primary_key=True)
    venue = Column(Integer, ForeignKey('team.id'))
    section = Column(Integer)
    row = Column(Integer)
    number = Column(Integer)
    tickets = relationship('Ticket')
    UniqueConstraint('venue', 'section', 'row', 'number')

#---------------------------------------------------------------

db_urls = {
    'postgres': 'postgresql:///%s' % db_name,
    'sqlite': 'sqlite:///%s.db' % db_name
}
engine = create_engine(db_urls[engine_type])
Base.metadata.create_all(engine)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

def engine_version():
    if engine_type == 'postgres':
        from psycopg2 import __version__
        return 'psycopg2 (%s)' % __version__
    if engine_type == 'sqlite':
        from sqlite3 import version
        return 'SQLite3 (%s)' % version

def set_prompt(ps):
    sys.ps1 = "\n%s->>> " % ps
    sys.ps2 = " " * len(str(ps)) +  " ... "

# set_prompt(db_name)

def alchemy_version():
    from sqlalchemy import __version__
    return 'SQL Alchemy (%s)' % __version__

startup_info = alchemy_version() + '\n' + str(engine) + '\n'

if __name__ == '__main__':
    print startup_info

