
from options import engine_type
from subprocess import check_output
import sys

fmt_str = '%s: %s'

# dict2xml has no version information available
deps = {
    'oauth2client': '__version__',
    'werkzeug': '__version__',
    'dict2xml': '__name__',
    'flask': '__version__',
    'sqlalchemy': '__version__',
    'sqlite3': 'version', 
    'psycopg2': '__version__'
} 

def check_dep(mod):
    try:
        m = __import__(mod)
        print fmt_str % (mod, m.__dict__[deps[mod]])
    except:
        print '%s not found' % mod 

if __name__ == '__main__':

    print fmt_str % ('python', str.split(sys.version, ' ')[0])
    print fmt_str % ('postgresql', str.split(check_output(['psql', '--version']).strip(),' ')[2])

    for mod in deps:
        check_dep(mod)
