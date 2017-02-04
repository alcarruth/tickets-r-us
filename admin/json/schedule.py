#!/usr/bin/python
# -*- coding: utf-8 -*-


# ok, I'm not sure what I'm doing yet.
# I need generate some sort of a football schedule

# so let's start with a couple of assumptions:
# 10 teams, round robin, everybody plays 9 games
# over 9 weeks.  

# We don't need to give the teams names yet,
# just take them from range(10)


num_teams = 10
teams = range(num_teams)

weeks = []
for i in range(num_teams-1):
    weeks.append([])

class Game:

    def __init__(self, home_team, visiting_team, week):
        self.home_team = home_team
        self.visiting_team = visiting_team
        self.week = week

    def __repr__(self):
        return str((self.home_team, self.visiting_team))

for i in range(len(weeks)):
    for j in range(num_teams/2):
        team_a = teams[j]
        team_b = teams[num_teams-j-1]
        if i%2>0:
            game = Game(team_b, team_a, i)
        else:
            game = Game(team_a, team_b, i)
        weeks[i].append(game)
    teams = teams[0:1] + teams[num_teams-1:num_teams] + teams[1:num_teams-1]

for i in range(len(weeks)):
    s = "week %d:" % i
    for game in weeks[i]:
        s += " " + str(game)
    print s


