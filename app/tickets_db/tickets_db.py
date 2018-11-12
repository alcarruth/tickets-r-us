#!/usr/bin/python -i
# -*- coding: utf-8 -*-

import json
from sqlalchemy import Column, ForeignKey, Integer, String, Date, create_engine, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, backref
from sqlalchemy.ext.hybrid import hybrid_property

import settings

Base = declarative_base()

#---------------------------------------------------------------
# Conference - a collection of Teams
# 
class Conference(Base):
    __tablename__ = 'conference'
   
    abbrev_name = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    logo = Column(String, nullable=False)

    def __repr__(self):
        return self.name

    def to_dict(self):
        return {
            'db_table': self.__tablename__,
            'values': {
                'abbrev_name': self.abbrev_name,
                'name': self.name,
                'logo': self.logo
            }
        }
        
#---------------------------------------------------------------
# Teams

class Team(Base):
    __tablename__ = 'team'

    id = Column(Integer, primary_key = True)
    name =Column(String, unique=True, nullable = False)
    nickname = Column(String)
    espn_id =  Column(Integer)
    city =  Column(String)
    state = Column(String)
    conference_name = Column(String, ForeignKey('conference.abbrev_name'))
    conference = relationship('Conference', backref=backref('teams', cascade="all, delete-orphan"))
    logo = Column(String)
    
    def to_dict(self):
        return {
            'db_table': self.__tablename__,
            'values': {
                'id': self.id,
                'name': self.name,
                'nickname': self.nickname,
                'espn_id': self.espn_id,
                'city': self.city,
                'state': self.state,
                'conference': self.conference
            }
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
     
    def to_dict(self):
        return {
            'db_table': self.__tablename__,
            'values': {
                'id': self.id,
                'home_team': self.home_team.name,
                'visiting_team': self.visiting_team.name,
                'date': self.date.isoformat()
            }
        }

    def __repr__(self):
        s ="%s at %s on %s" % (self.visiting_team, self.home_team, self.date.isoformat())
        return s
 
#---------------------------------------------------------------
# User - someone with a ticket they're trying to sell

class User(Base):
    __tablename__ = 'ticket_user'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    picture = Column(String, nullable=True)

    def to_dict(self):
        d = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
        }
        if self.picture:
            d['picture'] = self.picture
        return {
            'db_table': self.__tablename__,
            'values': d
        }

    def __repr__(self):
        return "%s <%s>" % (self.name, self.email)

# add a user to the database
#
def createUser(db_session, user_data):
    user = User(
        name = user_data["name"],
        email = user_data["email"],
        picture = user_data["picture"]
    )
    db_session.add(user)
    db_session.commit()
    return user

# maps a user_id to a user
#
def getUserByID(db_session, user_id):
    try:
        return db_session.query(User).filter_by(id=user_id).one()
    except:
        return None

# lookup a user by their email address
# and return the user id
#
def getUserByEmail(db_session, email):
    try:
        return db_session.query(User).filter_by(email=email).one()
    except:
        return None


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
    user_id = Column(Integer, ForeignKey('ticket_user.id'))
    seller = relationship(User, backref=backref('ticket_lots'))
    game_id = Column(Integer, ForeignKey('game.id'))
    game = relationship(Game, backref=backref('ticket_lots',  cascade="all, delete-orphan"))
    section = Column(Integer)
    row = Column(Integer)
    price = Column(Integer) # $ per ticket
    img_path = Column(String)

    def make_img_path(self, img_type):
        return 'static/images/ticket_images/ticket_lot_%d.%s' % (self.id, img_type)

    def seats(self):
        return [ ticket.seat for ticket in self.tickets ]

    def num_seats(self):
        return len(self.tickets)

    def seats_str(self):
        return ', '.join(map(str,self.seats()))

    def to_dict(self):
        return {
            'db_table': self.__tablename__,
            'values': {
                'id': self.id,
                'game_id': self.game_id,
                'seller_id': self.seller_id,
                'section': self.section,
                'row': self.row,
                'price': self.price,
                'seats': self.seats()
            }
        }

    def __repr__(self):
        s = str(self.game)
        s += " [sec: %d, row: %d, seats: %s]" % (self.section, self.row, self.seats())
        s += " $%d ea" % self.price
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
    lot = relationship(Ticket_Lot, backref=backref('tickets', cascade="all, delete-orphan"))
    seat = Column(Integer)
    #UniqueConstraint('game', 'section', 'row', 'seat')

    def to_dict(self):
        return {
            'db_table': self.__tablename__,
            'values': {
                'id': self.id,
                'game': self.lot.game,
                'section': self.lot.section,
                'row': self.lot.row,
                'seat': self.seat,
                'price': self.lot.price
            }
        }

    def __repr__(self):
        s = str(self.lot.game)
        s += " [sec: %d, row: %d, seat: %d]" % (self.lot.section, self.lot.row, self.seat)
        s += " $%d" % self.lot.price
        return s

#---------------------------------------------------------------

# For postgresql the db user will be the user asssociated with the
# current python process.  See postgresql configuration files pg_hba.conf
# and pg_ident.conf for more information.
#
db_urls = {
    'postgres': 'postgresql:///%s' % settings.db_name,
    'sqlite': 'sqlite:///%s.db' % settings.db_name
}
engine = create_engine(db_urls[settings.engine_type])
Base.metadata.create_all(engine)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

def engine_version():
    if settings.engine_type == 'postgres':
        from psycopg2 import __version__
        return 'psycopg2 (%s)' % __version__
    if settings.engine_type == 'sqlite':
        from sqlite3 import version
        return 'SQLite3 (%s)' % version

def set_prompt(ps):
    sys.ps1 = "\n%s->>> " % ps
    sys.ps2 = " " * len(str(ps)) +  " ... "

# set_prompt(settings.db_name)

def alchemy_version():
    from sqlalchemy import __version__
    return 'SQL Alchemy (%s)' % __version__

startup_info = "Tickets'R'Us Web App\n" + str(engine) + '\n'

def show_tickets(user):
    print user
    for ticket in user.tickets:
        print ticket
