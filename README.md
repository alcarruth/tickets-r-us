## Udacity FSND Project 3 Item Catalog

### Quick Start

#### Pre-requisites

Download the project as follows:

```
$ git clone https://github.com/alcarruth/fullstack-p3-item-catalog.git
$ cd fullstack-p3-item-catalog
```

This project requires a number of supporting modules and has been built
and tested with the following versions:

 - python: 2.7.6
 - postgresql: 9.3.11
 - sqlite3: 2.6.0
 - psycopg2: 2.4.5
 - pip: 1.5.4

The above can be installed (on Linux) using apt-get:

```
$ sudo apt-get install postgresql sqlite3 python-psycopg2 python-pip
```

 - dict2xml: 1.4
 - sqlalchemy: 1.0.9
 - flask: 0.10.1
 - flask-seasurf: 0.2.2
 - werkzeug: 0.11.4
 - oauth2client: 1.5.2

You can check/install these modules on your system by issuing
the command:

```
$ sudo pip install -r requirements.txt
```

Next, edit the `options.py` file to suit your situation.  In particular, the
variable `engine-type` should be set to the db backend of your choice.
The code has been tested and seems to work well with postgresql 9.3.11
and with sqlite 2.6.0.  Once this is done,
rebuild the database using the script `reset_db.sh`.  With the default
dummy data table sizes, this takes a few seconds and produces
something like the following terminal output:

```
$ ./reset_db.sh 
DROP DATABASE
CREATE DATABASE
removed ‘tickets.db’
loading 10 conferences
loading 128 teams
schecduling 77 games
schecduling 66 games
schecduling 77 games
schecduling 66 games
schecduling 77 games
schecduling 71 games
schecduling 71 games
schecduling 66 games
schecduling 66 games
schecduling 66 games
creating 1000 users
creating 5000 ticket lots
0
1000
2000
3000
4000
created 13793 tickets
```

Now the db has been initialized and you can run the ticket app server:

```
$ ./web_server.py 
 * Running on http://0.0.0.0:5000/
 * Restarting with reloader
```

Point your browser to `http://localhost:5000` to view the Tickets'R'Us 
web app.


### Project Overview

This project implements a basic ticket broker website for college football games.
A user can select a conference, select a game from the conference teams' schedules
and view tickets available for purchase.  The tickets are organized into 'ticket lots'
which are owned by a user.  These ticket lots can be edited and deleted only by the
owning user.  New ticket lots for sale can be added by any logged in user.

#### Dummy Data

A significant portion of the work involved setting up 'dummy data' to populate
the database with conferences, teams, games, schedules, tickets and users.  I have
used the conferences from NCAA Division 1 football with a slight modification:
Notre Dame and BYU have been moved to the Big 12 Conference and Army has been
moved to the Sun Belt Conference.  This was done in an attempt to even the 
sizes of the conferences and give them each at least 12 teams.  The logo
images for the teams were shamelessly purloined from the ESPN website.  Of course
they are registered trademarks of their respective institutions and cannot
be used without permission.  I thought I'd be ok including them in this strictly
academic exercise.

The initialization program `init_tickets.py` adds the conferences and the
teams to the database and then randomly generates game schedules for each
team using a round robin algorithm for each conference.  Each team plays
11 games.

The initialization program then randomly generates a large number of dummy
users with dummy email addresses, and then a large number of ticket_lots
with tickets to randomly selected games and being offered by randomly selected
users.

#### Using the Tickets 'R' Us Website

#### Step 1 - Choose a conference

The Tickets 'R' Us home page presents the user with a list of conferences, each in 
an oulined box containing a list of teams in the conferences.  Clicking anywhere
in the box will bring up the conference page.

![alt text](https://raw.githubusercontent.com/alcarruth/fullstack-p3-item-catalog/tickets/admin/images/jpg/tickets_step1.jpg "main page")

#### Step 2 - Choose a game

On the conference page the user is presented with the schedules for each team in the 
conference.  Clicking on a game in a schedule will bring up a page with the ticket lots
available for that game.

![alt text](https://raw.githubusercontent.com/alcarruth/fullstack-p3-item-catalog/tickets/admin/images/jpg/step2.jpg "step 2")

#### Game Page

The game page displays the ticket lots available for that game.  The ticket lots are 
collections of tickets (intended to be adjacent seats) in numbers of 1, 2 and 4.


![alt text](https://raw.githubusercontent.com/alcarruth/fullstack-p3-item-catalog/tickets/admin/images/jpg/game_tickets.jpg "game tickets")

#### Tickets Page

The tickets page displays the data associated with a ticket lot, i.e. the tickets, the user (seller),
the user's email address and the price per ticket.  Actual ticket purchasing is not implemented.
(So a fictitious buyer must contact the fictitious seller at the fictitious email address in order
to buy the fictitious tickets !-)

![alt text](https://raw.githubusercontent.com/alcarruth/fullstack-p3-item-catalog/tickets/admin/images/jpg/ticket_lot.jpg "ticket lot")

#### Logging In

In order to sell tickets a user must first be logged in.  We offer two methods for logging in: via Google and via Facebook.

![alt text](https://raw.githubusercontent.com/alcarruth/fullstack-p3-item-catalog/tickets/admin/images/jpg/login.jpg "login")

Once logged in the user's name appears next to the logout button in the header.
![alt text](https://raw.githubusercontent.com/alcarruth/fullstack-p3-item-catalog/tickets/admin/images/jpg/logged_in.jpg "logged in")

#### Selling Tickets

To sell tickets, a user must be logged in.  If they are logged in, clicking the sell button brings up a form
where they can enter the data for the ticket lot.

![alt text](https://raw.githubusercontent.com/alcarruth/fullstack-p3-item-catalog/tickets/admin/images/jpg/sell_tickets.jpg "sell tickets")

#### User Page

Clicking on the user's name brings up the User Page which shows the user's name, email address and a table
of the ticket lots the user has listed for sale.

![alt text](https://raw.githubusercontent.com/alcarruth/fullstack-p3-item-catalog/tickets/admin/images/jpg/my_tickets.jpg "my tickets")

#### User's Ticket Lot Page

On the Tickets page, and if the logged in user is the owner of the tickets, there are buttons to edit 
and to delete the ticket lot.  Editing is restricted to the price.  You can't change the section, row or seat numbers.
To do this you would first have to delete the lot and enter them again with the correct data.

![alt text](https://raw.githubusercontent.com/alcarruth/fullstack-p3-item-catalog/tickets/admin/images/jpg/my_ticket_lot.jpg "my ticket lot")

#### Deleting tickets page:
![alt text](https://raw.githubusercontent.com/alcarruth/fullstack-p3-item-catalog/tickets/admin/images/jpg/delete_tickets.jpg "delete tickets")

#### Editing Tickets Page
![alt text](https://raw.githubusercontent.com/alcarruth/fullstack-p3-item-catalog/tickets/admin/images/jpg/edit_tickets.jpg "edit tickets")



### License

Probably GNU or MIT or BSD ... I don't know.
