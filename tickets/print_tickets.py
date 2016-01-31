#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from tickets import Conference, Team, DBSession, startup_info
import random

session = DBSession()

f = open('templates/main.html')
main_template = f.read()
f.close()

f = open('templates/ticket.html')
ticket_template = f.read()
f.close()

def team_logo(team):
    logo = "static/images/" + team.name + '_' + team.nickname + '.png'
    logo = logo.replace(' ','_').lower()
    return logo

def print_tickets(teams):
    tickets = ''
    random.shuffle(teams)
    if len(teams) % 2:
        teams = teams[0:-1]
    for i in range(0,len(teams),2):
        visitor = teams[i]
        home = teams[i+1]
        tickets += ticket_template.format(
            visitors_logo = visitor.logo,
            visitors_name = visitor.name,
            visitors_nickname = visitor.nickname,
            home_team_logo = home.logo,
            home_team_name = home.name,
            home_team_nickname = home.nickname)
    return tickets
        
def print_ticket_page():
    body = ''
    conferences = session.query(Conference).all()
    for conference in conferences:
        body += '<div class="conference">\n'
        body += '<h1> %s </h1>\n' % conference.name
        #body += '<img src="static/conference_logos/%s">' % conference.logo
        body += print_tickets(conference.teams)
        body += '</div>\n'
        #body += '<hr>\n'
        body += '<!-- ------------------------------------'
        body += '------------------------------------- -->'
        body += '\n\n\n'
    page = main_template.format(
        title = "Tickets",
        body = body)
    f = open('tickets.html', 'w')
    f.write(page)
    f.close()

if __name__ == '__main__':
    print_ticket_page()


    
    
