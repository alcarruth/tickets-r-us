#!/usr/bin/python
# -*- coding: utf-8 -*-

# The team logos were shamelessly purloined from the ESPN website, and 
# they remain the property of their respective institutions.  They
# are included here only for the purposes of this academic exercise and
# should not be used with out the consent of their owners.

import json
from tickets import Conference, Team, DBSession, startup_info
import urllib2
session = DBSession()

espn_img_url = "http://a.espncdn.com/combiner/i?img=/i/teamlogos/ncaa/500/%s.png"

teams = session.query(Team).all()

for team in teams:
    espn_id = str(team.espn_id)
    img = urllib2.urlopen(espn_img_url % espn_id).read()
    fname = 'images/' + team.name + '_' + team.nickname + '.png'
    fname = fname.replace(' ','_').lower()
    f = open(fname, 'wb')
    f.write(img)
    f.close()
    print fname

    
