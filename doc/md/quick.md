## Tickets'R'Us

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
 - requests: 2.21.0
 - psycopg2-binary: 2.7.7
 - uwsgi: 2.0

You can check/install these modules on your system by issuing
the command:

```
$ sudo pip install -r admin/requirements.pip
```

Next, edit the `settings.py` file to suit your situation.  In particular, the
variable `engine-type` should be set to the db backend of your choice.
The code has been tested and seems to work well with postgresql 9.3.11
and with sqlite 2.6.0.  Once this is done,
rebuild the database using the script `reset_db.sh`.  With the default
dummy data table sizes, this takes a few seconds and produces
something like the following terminal output:

```
$ ./app/reset_db.sh 
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
