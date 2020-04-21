#!/usr/bin/env coffee
# -*- coding: utf-8 -*-

{ Client, Pool } = require('pg')

settings =

  # app settings
  app_dir: '/var/www/git/udacity/tickets/app/'

  google_secrets_file: 'conf/google.json'
  facebook_secrets_file: 'conf/facebook.json'

  # must match setting in reset_db.sh 
  db_name: 'tickets'

  # options for dummy data creation
  year: 2016
  number_of_gamee: 11
  number_of_users: 1000
  
  # This is the number of ticket _lots_.
  # The actual number of tickets created will 
  # be 2 or 3 times this amount.
  number_of_ticket_lots: 5000


pool = new Pool(host: '/var/run/postgresql', database: 'tickets')


#---------------------------------------------------------------
# Conference - a collection of Teams
# 
class Conference

  constructor: ->
    @tablename = 'conference'
    @abbrev_name = Column(String, primary_key=True)
    @name = Column(String, unique=True, nullable=False)
    @logo = Column(String, nullable=False)

  toString: =>
    return @name

  to_dict: =>
    db_table: @tablename
    values: 
      abbrev_name: @abbrev_name
      name: @name
      logo: @logo

        
#---------------------------------------------------------------
# Teams

class Team

  constructor: (json) ->

    @spec =
      table_name: 'Team'
      id: 'Column(Integer, primary_key = True)'
      name: 'Column(String, unique=True, nullable = False)'
      nickname: 'Column(String)'
      logo: 'Column(String)'
      espn_id:  'Column(Integer)'
      city:  'Column(String)'
      state: 'Column(String)'
      conference_name: 'Column(String, ForeignKey("conference.abbrev_name"))'
      conference: 'relationship("Conference", backref=backref("teams", cascade="all, delete-orphan"))'

    @values = {}
    for k,v of JSON.parse(json)
      @values = v
      
  to_dict: =>
    db_table: @tablename
    values:
      id: @id
      name: @name
      nickname: @nickname
      espn_id: @espn_id
      city: @city
      state: @state
      conference: @conference

  schedule: =>
    games = @away_games + @home_games
    games.sort(key = lambda x: x.date)
    return games

  dates: =>
    games = @away_games + @home_games
    ds = map(lambda x: x.date, games)
    ds.sort()
    return ds

  toString: =>
    return @name

#---------------------------------------------------------------
# Games - a pairing of Teams
# - the venue is the stadium of the home team
#
# TODO: generalize Game to 'Event'
# - add field for event_type, e.g. 'football_game', 'concert'
# - maybe Football_Game is a subclass of Event?
#   home_team and visiting_team make no sense for general Event
# 
class Game

  constructor: ->

    @tablename = 'game'
    @id = Column(Integer, primary_key=True)
    @home_team_id = Column(Integer, ForeignKey('team.id'))
    @home_team = relationship(Team, foreign_keys=[home_team_id], backref=backref('home_games'))
    @visiting_team_id = Column(Integer, ForeignKey('team.id'))
    @visiting_team = relationship(Team, foreign_keys=[visiting_team_id], backref=backref('away_games'))
    @date = Column(Date, nullable=False)
     
  to_dict: =>
    db_table: @tablename
    values:
      id: @id,
      home_team: @home_team.name,
      visiting_team: @visiting_team.name,
      date: @date.isoformat()

  toString: =>
    s ="%s at %s on %s" % (@visiting_team, @home_team, @date.isoformat())
    return s
 
#---------------------------------------------------------------
# User - someone with a ticket they're trying to sell

class User

  constructor: ->
    @__tablename__ = 'ticket_user'
    @id = Column(Integer, primary_key=True)
    @name = Column(String, nullable=False)
    @email = Column(String, unique=True, nullable=False)
    @picture = Column(String, nullable=True)

  to_dict: =>
    d = { id: @id, name: @name, email: @email }
    d.picture = @picture if @picture
    return 
      db_table: @__tablename__
      values: d

  toString: =>
    return "%s <%s>" % (@name, @email)


# add a user to the database
#
createUser = (db_session, user_data) ->
    user = new User(
        name = user_data["name"],
        email = user_data["email"],
        picture = user_data["picture"])
    db_session.add(user)
    db_session.commit()
    return user

# maps a user_id to a user
#
getUserByID = (db_session, user_id) ->
  try
    return db_session.query(User).filter_by(id=user_id).one()
  catch error
    return None

# lookup a user by their email address
# and return the user id
#
getUserByEmail = (db_session, email) ->
  try
    return db_session.query(User).filter_by(email=email).one()
  catch error
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

class Ticket_Lot

  constructor: ->
    @__tablename__ = 'ticket_lot'
    @id = Column(Integer, primary_key=True)
    @user_id = Column(Integer, ForeignKey('ticket_user.id'))
    @seller = relationship(User, backref=backref('ticket_lots'))
    @game_id = Column(Integer, ForeignKey('game.id'))
    @game = relationship(Game, backref=backref('ticket_lots',  cascade="all, delete-orphan"))
    @section = Column(Integer)
    @row = Column(Integer)
    @price = Column(Integer) # $ per ticket
    @img_path = Column(String)

  make_img_path: (img_type) =>
    return 'static/images/ticket_images/ticket_lot_%d.%s' % (@id, img_type)

  seats: =>
    return [ ticket.seat for ticket in @tickets ]

  num_seats: =>
    return len(@tickets)

  seats_str: =>
    return ', '.join(map(str,@seats()))

  to_dict: =>
    db_table: @__tablename__,
    values: 
      id: @id,
      game_id: @game_id,
      seller_id: @seller_id,
      section: @section,
      row: @row,
      price: @price,
      seats: @seats()

  toString: =>
    s = str(@game)
    s += " [sec: %d, row: %d, seats: %s]" % (@section, @row, @seats())
    s += " $%d ea" % @price
    return s


#---------------------------------------------------------------
# Tickets - a seat at a Game
#
# TODO: We're assuming that the home team uniquely identifies the
# venue for the game, but games are sometimes played at neutral sites.

class Ticket

  constructor: ->
    @__tablename__ = 'ticket'
    @id = Column(Integer, primary_key=True)
    @lot_id = Column(Integer, ForeignKey('ticket_lot.id'))
    @lot = relationship(Ticket_Lot, backref=backref('tickets', cascade="all, delete-orphan"))
    @seat = Column(Integer)
    #UniqueConstraint('game', 'section', 'row', 'seat')

  to_dict: =>
    db_table: @__tablename__,
    values:
      id: @id,
      game: @lot.game,
      section: @lot.section,
      row: @lot.row,
      seat: @seat,
      price: @lot.price

  toString: =>
    s = str(@lot.game)
    s += " [sec: %d, row: %d, seat: %d]" % (@lot.section, @lot.row, @seat)
    s += " $%d" % @lot.price
    return s

#---------------------------------------------------------------

# For postgresql the db user will be the user asssociated with the
# current python process.  See postgresql configuration files pg_hba.conf
# and pg_ident.conf for more information.
#
db_urls =
  postgres: 'postgresql:///%s' % settings.db_name,
  sqlite: 'sqlite:///%s.db' % settings.db_name

engine = create_engine(db_urls[settings.engine_type])
Base.metadata.create_all(engine)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

engine_version = ->
  if settings.engine_type == 'postgres'
    #from psycopg2 import __version__
    #return 'psycopg2 (%s)' % __version__
  if settings.engine_type == 'sqlite'
    #from sqlite3 import version
    #return 'SQLite3 (%s)' % version

set_prompt: (ps) ->
  sys.ps1 = "\n%s->>> " % ps
  sys.ps2 = " " * len(str(ps)) +  " ... "

# set_prompt(settings.db_name)

startup_info = "Tickets'R'Us Web App\n" + str(engine) + '\n'

show_tickets = (user) ->
  console.log(user)
  for ticket in user.tickets
    console.log(ticket)
