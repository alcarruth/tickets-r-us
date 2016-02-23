#!/usr/bin/python -i
# -*- coding: utf-8 -*-

import json
from sqlalchemy import Column, ForeignKey, Integer, String, Date, create_engine, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, backref
from sqlalchemy.ext.hybrid import hybrid_property


# OPTIONS
#engine_type = 'postgres'
engine_type = 'sqlite'

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

    def serialize(self):
        d = {}
        d['abbrev_name'] = self.abbrev_name
        d['name'] = self.name
        d['logo'] = self.logo
        return d
        
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
            'conference': self.conference
        }

    def schedule(self):
        games = self.away_games + self.home_games
        games.sort(key = lambda x: x.date)
        return games

    def dates(self):
        games = self.away_games + self.home_games
        ds = map(lambda x: x.date, games)
        ds.sort()
        return ds

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
    home_team_id = Column(Integer, ForeignKey('team.id'))
    home_team = relationship(Team, foreign_keys=[home_team_id], backref=backref('home_games'))
    visiting_team_id = Column(Integer, ForeignKey('team.id'))
    visiting_team = relationship(Team, foreign_keys=[visiting_team_id], backref=backref('away_games'))
    date = Column(Date, nullable=False)
    #tickets = relationship('Ticket')
    
    def __repr__(self):
        s ="%s at %s on %s" % (self.visiting_team, self.home_team, self.date.isoformat())
        return s
 
#---------------------------------------------------------------
# User - someone with a ticket they're trying to sell

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    picture = Column(String, nullable=True)

    def __repr__(self):
        return "%s <%s>" % (self.name, self.email)


#---------------------------------------------------------------
# 
# TODO: Previously, the Ticket class had the game, section, row
# and seat number fields, and these were constrained to be unique.
# That is, there can be at most one ticket for each seat in each
# row in each section for any game.  Simple enough.
# But I wanted this Ticket_Lot class to handle tickets to be sold
# as a group.  Normally this means seats adjacent to each other
# for the same game.

class Ticket_Lot(Base):
    __tablename__ = 'ticket_lot'

    id = Column(Integer, primary_key=True)
    seller_id = Column(Integer, ForeignKey('user.id'))
    seller = relationship(User, backref=backref('ticket_lots'))
    game_id = Column(Integer, ForeignKey('game.id'))
    game = relationship(Game, backref=backref('ticket_lots'))
    section = Column(Integer)
    row = Column(Integer)
    price = Column(Integer) # $ per ticket

    def seats(self):
        return [ ticket.seat for ticket in self.tickets ]

    def num_seats(self):
        return len(self.tickets)

    def seats_str(self):
        return ', '.join(map(str,self.seats()))

    def serialize(self):
        return {
            'game': self.game,
            'section': self.section,
            'row': self.row,
            'price': self.price,
            'seats': self.seats()
        }

    def __repr__(self):
        s = str(self.game)
        s += " [sec: %d, row: %d, seats: %s]" % (self.section, self.row, self.seats())
        s += " $%d ea" % self.price()
        return s


#---------------------------------------------------------------
# Tickets - a seat at a Game
#
# TODO: We're assuming that the home team uniquely identifies the
# venue for the game, but games are sometimes played at neutral sites.

class Ticket(Base):
    __tablename__ = 'ticket'

    id = Column(Integer, primary_key=True)
    lot_id = Column(Integer, ForeignKey('ticket_lot.id'))
    lot = relationship(Ticket_Lot, backref=backref('tickets'))
    seat = Column(Integer)
    #UniqueConstraint('game', 'section', 'row', 'seat')

    def serialize(self):
        return {
            'game': self.lot.game,
            'section': self.lot.section,
            'row': self.lot.row,
            'seat': self.seat,
            'price': self.lot.price
        }

    def __repr__(self):
        s = str(self.lot.game)
        s += " [sec: %d, row: %d, seat: %d]" % (self.lot.section, self.lot.row, self.seat)
        s += " $%d" % self.lot.price
        return s

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

def show_tickets(user):
    print user
    for ticket in user.tickets:
        print ticket

if __name__ == '__main__':
    print startup_info

    session = DBSession()
    conferences = session.query(Conference).all()
    tickets = session.query(Ticket).all()
    games = session.query(Game).all()
    users = session.query(User).all()
    teams = session.query(Team).all()
