#!/usr/bin/python
# -*- coding: utf-8 -*-

# init_tickets.py
#
# This file is used to populate the tickets database.
# It is called by the reset_db.sh script.
# Options for the sizes of the tables etc are included in
# settings.py.

import json
import datetime
import random

from tickets_db import Conference, Team, Game, Ticket, Ticket_Lot, User
from tickets_db import DBSession, startup_info
from settings import year, number_of_games, number_of_users, number_of_ticket_lots

def team_logo(team):
    logo = "/images/team_logos/" + team['name'] + '_' + team['nickname'] + '.png'
    logo = logo.replace(' ','_').lower()
    return logo

def load_teams_from_json():
    #f = open('json/teams.json')
    f = open('json/teams_new.json')
    teams = json.load(f)
    f.close()
    print "loading %d teams" % len(teams)
    for team in teams:
        session.add( Team(
            conference_name = team['conference'].replace(' ','_'),
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
    print "loading %d conferences" % len(conferences)
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

# full round_robin for n competitors
# returns a list of triples (c, d, r)
# meaning c plays d in round r
#
def round_robin_index(n):
    cs = range(n)
    odd = n%2
    if odd:
        n += 1
        cs.insert(0, -1)
    schedule = []
    for r in range(n-1):
        for j in range(odd, n/2):
            c = cs[j]
            d = cs[n-j-1]
            schedule.append((c, d, r))
        cs = cs[0:1] + cs[n-1:n] + cs[1:n-1]
    return schedule

def schedule_games(teams, dates):
    teams = teams[:]
    random.shuffle(teams)
    print "schecduling %d games" % (len(teams) * len(dates) /2)
    for (c,d,r) in round_robin_index(len(teams)):
        if r%2:
            (c,d) = (d,c)
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

    print "creating %d users" % n
    for i in range(n):
        first_name = random.choice(male_names + female_names)
        last_name = random.choice(surnames)
        name = '%s %s' % (first_name, last_name)
        email = first_name[0] + last_name + str(random.choice(range(10000,100000))) + '@gmail.com'
        picture = None
        session.add( User(
            name = name,
            email = email,
            picture = picture
        ))
    session.commit()

# n is the number of ticket _lots_ to add to the database
# the actual number of tickets will be more than that. 
def create_tickets(n):
    users = session.query(User).all()
    games = session.query(Game).all()

    print "creating %d ticket lots" % n
    num_tickets = 0
    for i in range(n):
        game = random.choice(games)
        seller = random.choice(users)
        section = random.randint(1,56)
        row = random.randint(1,45)
        seat = random.randint(1,30)
        num_seats = random.choice([1,2,2,2,2,4,4,4,4])
        price = random.choice([35,40,50,52,55,58,65,67,70,72,74,78,85,88,100,110,120,195,250,300])
        try:
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
            num_tickets += num_seats

        except:
            session.rollback()

        if i%1000 == 0:
            print i
            session.commit()
    session.commit()
    print "created %d tickets" % num_tickets


def populate_db():
    load_conferences_from_json()
    load_teams_from_json()
    dates = get_saturdays(year, number_of_games)
    for conf in session.query(Conference).all():
        schedule_games(conf.teams, dates)
    create_users(number_of_users)
    create_tickets(number_of_ticket_lots)


if __name__ == '__main__':
    print startup_info
    session = DBSession()
    populate_db()
    session.close()
