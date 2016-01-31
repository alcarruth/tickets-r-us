#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from tickets import Conference, Team, Game, Seat, Ticket, Seller
from tickets import DBSession, startup_info


def team_logo(team):
    logo = "static/images/" + team['name'] + '_' + team['nickname'] + '.png'
    logo = logo.replace(' ','_').lower()
    return logo

def load_teams_from_json():
    f = open('teams.json')
    teams = json.load(f)
    f.close()
    for team in teams:
        session.add( Team(
            conference = team['conference'],
            city = team['city'],
            espn_id = team['espn_id'],
            state = team['state'],
            name = team['name'],
            nickname = team['nickname'],
            logo = team_logo(team)
        ))
        session.commit()

def load_conferences_from_json():
    f = open('conferences.json')
    conferences = json.load(f)
    f.close()
    for conference in conferences:
        session.add( Conference(
            abbrev_name = conference['abbrev_name'],
            name = conference['name'],
            logo = conference['logo']
        ))
        session.commit()

def create_seats():
    for venue in teams:
        for section in map(chr, range(ord('A'), ord('Z')+1)):
            for row in range(1, 50):
                for number in range(1,30):
                    session.add( Seat(
                        venue = venue,
                        section = section,
                        row = row,
                        number = number
                    ))
                    session.commit()
    

session = DBSession()
load_conferences_from_json()
load_teams_from_json()


