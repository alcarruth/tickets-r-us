
from options import engine_type

try:
    import dict2xml
    print 'dict2xml version %s' % 'unknown'
except:
    print 'dict2xml not installed'

try:
    import flask
    print 'flask version %s' % flask.__version__
except:
    print 'flask not installed'

try:
    import sqlalchemy
    print 'sqlalchemy version %s' % sqlalchemy.__version__
except:
    print 'sqlalchemy not installed'

#try: 
#    import postgresql
#    print 'postgresql version %s' % postgresql.__version__
#except:
#    print 'postgresql not installed'

if engine_type == 'sqlite':
    try:
        import sqlite3
        print 'sqlite3 version %s' % sqlite3.version
    except:
        print 'sqlite3 not installed'

if engine_type == 'postgres':
    #try: 
    #    import postgresql
    #    print 'postgresql version %s' % postgresql.__version__
    #except:
    #    print 'postgresql not installed'

try: 
    import psycopg2
    print 'psycopg2 version: %s' % psycopg2.__version__
except:
    print 'psycopg2 not installed'

