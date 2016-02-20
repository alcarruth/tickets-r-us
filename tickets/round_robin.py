#!/usr/bin/python -i
# -*- coding: utf-8 -*-

# full round_robin for n competitors
# returns a list of triples (c, d, r)
# meaning c plays d in round r
#
def round_robin_index(n):
    cs = range(n)
    schedule = []
    for r in range(n-1):
        for j in range(n/2):
            c = cs[j]
            d = cs[n-j-1]
            schedule.append((c, d, r))
        cs = cs[0:1] + cs[n-1:n] + cs[1:n-1]
    return schedule

# same as above but alternates the order
# of c and d each round.
#
def round_robin_alt(n):
    cs = range(n)
    schedule = []
    alt = False
    for r in range(n-1):
        for j in range(n/2):
            c = cs[j]
            d = cs[n-j-1]
            if alt:
                schedule.append((d, c, r))
            else:
                schedule.append((c, d, r))
        cs = cs[0:1] + cs[n-1:n] + cs[1:n-1]
        alt = not alt
    return schedule

