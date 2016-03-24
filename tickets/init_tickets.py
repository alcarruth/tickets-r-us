#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import datetime
from tickets import Conference, Team, Game, Seat, Ticket, Ticket_Lot, User
from tickets import DBSession, startup_info
from round_robin import round_robin_alt
from random import shuffle
import random

def team_logo(team):
    logo = "static/images/" + team['name'] + '_' + team['nickname'] + '.png'
    logo = logo.replace(' ','_').lower()
    return logo

def load_teams_from_json():
    #f = open('json/teams.json')
    f = open('json/teams_new.json')
    teams = json.load(f)
    f.close()
    for team in teams:
        session.add( Team(
            conference = team['conference'].replace(' ','_'),
            city = team['city'],
            espn_id = team['espn_id'],
            state = team['state'],
            name = team['name'],
            nickname = team['nickname'],
            logo = team_logo(team)
        ))
    session.commit()

def load_conferences_from_json():
    #f = open('json/conferences.json')
    f = open('json/conferences_new.json')
    conferences = json.load(f)
    f.close()
    for conference in conferences:
        session.add( Conference(
            abbrev_name = conference['abbrev_name'].replace(' ','_'),
            name = conference['name'],
            logo = conference['logo']
        ))
    session.commit()

# returns a list of n Saturdays
# starting on first Saturday in Sept of year
def get_saturdays(year, n):
    # set date to first Saturday in September
    sep1 = datetime.date(year, 9, 1)
    sat = sep1.replace(day = 1 + (5 - sep1.weekday()) % 7)
    dates = [sat]
    # add the next n-1 saturdays
    for i in range(n-1):
        # time delta 7 days
        sat = sat + datetime.timedelta(7)
        dates.append(sat)
    return dates

def schedule_games(teams, dates):
    teams = teams[:]
    random.shuffle(teams)
    for (c,d,r) in round_robin_alt(len(teams)):
        if r < len(dates):
            session.add( Game(
                home_team = teams[c],
                visiting_team = teams[d],
                date = dates[r]
            ))
    session.commit()

def load_names_from_json(name_root):
    f = open('json/' + name_root + '.json')
    names = json.loads(f.read()).keys()
    f.close()
    return names

def create_users(n):
    female_names = load_names_from_json('female_names')
    male_names = load_names_from_json('male_names')
    surnames = load_names_from_json('surnames')

    for i in range(n):
        first_name = random.choice(male_names + female_names)
        last_name = random.choice(surnames)
        name = '%s %s' % (first_name, last_name)
        email = first_name[0] + last_name + str(random.choice(range(1000,10000))) + '@gmail.com'
        session.add( User(
            name = name,
            email = email
        ))
    session.commit()

def create_tickets(n):
    users = session.query(User).all()
    games = session.query(Game).all()

    for i in range(n):
        game = random.choice(games)
        seller = random.choice(users)
        section = random.randint(1,56)
        row = random.randint(1,45)
        seat = random.randint(1,30)
        num_seats = random.choice([1,2,2,2,2,4,4,4,4])
        price = random.choice([35,40,50,52,55,58,65,67,70,72,74,78,85,88,100,110,120,195,250,300])
        ticket_lot = Ticket_Lot(
            seller = seller,
            game = game,
            section = section,
            row = row,
            price = price
        )
        session.add( ticket_lot)
        for j in range(num_seats):
            session.add( Ticket(
                lot = ticket_lot,
                seat = seat + j
            ))
    session.commit()

def populate_db():
    load_conferences_from_json()
    load_teams_from_json()
    dates = get_saturdays(2016, 11)
    for conf in session.query(Conference).all():
        schedule_games(conf.teams, dates)
    create_users(1000)
    create_tickets(10000)

session = DBSession()
populate_db()
session.close()
