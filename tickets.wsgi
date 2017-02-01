
import sys, os

app_dir = '/home/carruth/tickets'
os.chdir(app_dir)
sys.path.insert(0, app_dir)

from web_server import app as application
