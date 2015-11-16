#Main file
#Reads data from Bruins Full Schedule (CSV file) and imports data into Bruins2015 Database
#After importing into database, the score is added to my calendar

from datetime import date, datetime, timedelta
import mysql.connector
import csv
import httplib2
from apiclient import discovery
from oauth2client import client
from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run_flow
from googleapiclient import sample_tools
import sys, os, tempfile, logging
import mysql.connector
from mysql.connector import MySQLConnection, Error
from configparser import ConfigParser

# from __future__ import ( division, absolute_import, print_function, unicode_literals)

if sys.version_info >= (3,):
    import urllib.request as urllib2
    import urllib.parse as urlparse
else:
    import urllib2
    import urlparse

#Download File
def download_file(url, desc=None):
    BruinsPath = r'C:\Programming\Bruins2015 Database'
    os.chdir(BruinsPath)
    u = urllib2.urlopen(url)
    
    scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
    filename = os.path.basename(path)
    if not filename:
        filename = 'downloaded.file'
    if desc:
        filename = os.path.join(desc, filename)
        
    with open(filename, 'wb') as f:
        meta = u.info()
        meta_func = meta.getheaders if hasattr(meta, 'getheaders') else meta.get_all
        meta_length = meta_func("Content-Length")
        file_size = None
        if meta_length:
            file_size = int(meta_length[0])
        print("Downloading: {0} Bytes: {1}".format(url, file_size))
        
        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer: 
                break
            
            file_size_dl += len(buffer)
            f.write(buffer)
            
            status = "{0:16}".format(file_size_dl)
            if file_size:
                status += "   [{0:6.2f}%]".format(file_size_dl * 100 / file_size)
            status += chr(13)
            end = ""
            print status, end
        print
    return filename
 
url = 'http://bruins.nhl.com/schedule/full.csv'
filename = download_file(url)
print filename

#Read in and format file
os.chdir(r'C:\Programming\Bruins2015 Database')

def read_db_config(filename='config.ini', section='mysql'):
    parser = ConfigParser()
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        raise Exception('{0} not found in the{1} file'.format(section, filename))
    
    return db
        
with open('full.csv', 'r') as bruins:
    db_config = read_db_config()
    homeAway = ''
    opponent = ''
    read_file = csv.reader(bruins)
   
    for line in read_file: 
        if line[0] == 'START_DATE' or line[0] == '09/20/2015' or line[0]=='09/22/2015' or line[0]=='09/24/2015' or line[0]=='09/26/2015' or line[0]=='09/28/2015' or line[0] == '09/30/2015' or line[0] == '10/02/2015':
            continue
          
        day_played = line[0]
        game = line[3].split()
        length = len(game)
        
        if game[0] == 'Boston':
            homeAway = 'Away'
        else:
            homeAway = 'Home'
       
        if homeAway == 'Away':
            if length ==3:
                opponent = game[2]
                score = ''
                winLose = ''
            elif length == 4:
                opponent = game[2]+game[3]
                score = '' 
                winLose = ''
            elif length == 5:
                opponent = game[3]
                if game[1] > game[4]:
                    winLose = 'Win'
                    score = game[1]+game[2]+game[4]
                else:
                    winLose = 'Lose'
                    score = game[4]+game[2]+game[1]
            elif length == 6:
                opponent = game[3] + game[4]
                if game[1] > game[5]:
                    winLose = 'Win'
                    score = game[1]+game[2]+game[5]
                else:
                    winLose = 'Lose'
                    score = game[5]+game[2]+game[1]
        else:#HOME
            if length == 3:
                opponent = game[0]
                score = ''
                winLose = ''
            elif length == 4:
                opponent = game[0]+game[1]
                score = ''
                winLose =''
            elif length == 5:
                opponent = game[0]
                if game[1] > game[4]:
                    winLose = 'Lose'
                    score = game[1]+game[2]+game[4]
                else:
                    winLose = 'Win'
                    score = game[4]+game[2]+game[1]
            elif length == 6:
                opponent = game[0]+game[1]
                if game[2] > game[5]:
                    winLose = 'Lose'
                    score = game[2]+game[3]+game[5]
                else:
                    winLose = 'Win'
                    score = game[5]+game[3]+game[2]
                
        if opponent == 'Montreal':
            opponent = 'Montreal Canadiens'
        elif opponent == 'Winnipeg':
            opponent = 'Winnipeg Jets'
        elif opponent == 'Dallas':
            opponent = 'Dallas Stars'
        elif opponent == 'NyRangers':
            opponent = 'New York Rangers'
        elif opponent == 'StLouis':
            opponent = 'St. Louis Blues'
        elif opponent == 'NyIslanders':
            opponent = 'New York Islanders'
        elif opponent == 'Washington':
            opponent = 'Washington Capitals'
        elif opponent == 'Minnesota':
            opponent = 'Minnesota Wild'
        elif opponent == 'Nashville':
            opponent = 'Nashville Predators'
        elif opponent == 'LosAngeles':
            opponent = 'Los Angeles Kings'
        elif opponent == 'Vancouver':
            opponent = 'Vancouver Canucks'
        elif opponent == 'Pittsburgh':
            opponent = 'Pittsburgh Penguins'
        elif opponent == 'Chicago':
            opponent = 'Chicago Blackhawks'
        elif opponent == 'Ottawa':
            opponent = 'Ottawa Senators'
        elif opponent == 'TampaBay':
            opponent = 'Tampa Bay Lightning'
        elif opponent == 'Detroit':
            opponent = 'Detroit Red Wings'
        elif opponent == 'NewJersey':
            opponent = 'New Jersey Devils'
        elif opponent == 'Florida':
            opponent = 'Florida Panthers'
        elif opponent == 'SanJose':
            opponent = 'San Jose Sharks'
        elif opponent == 'Arizona':
            opponent = 'Arizona Coyotes'
        elif opponent == 'Carolina':
            opponent = 'Carolina Hurricanes'
        elif opponent == 'Buffalo':
            opponent = 'Buffalo Sabres'
        elif opponent == 'Philadelphia':
            opponent = 'Philadelphia Flyers'
        elif opponent == 'Edmonton':
            opponent = 'Edmonton Oilers'
        elif opponent == 'Colorado':
            opponent = 'Colorado Avalanche'
        elif opponent == 'Calgary':
            opponent = 'Calgary Flames'
        elif opponent == 'Toronto':
            opponent = 'Toronto Maple Leafs'
        elif opponent == 'Anaheim':
            opponent = 'Anaheim Ducks'
        elif opponent == 'Columbus':
            opponent = 'Columbus Blue Jackets'
                
        date_object = datetime.datetime.strptime(day_played, "%m/%d/%Y")
        day = date_object.strftime("%Y%m%d")
        
        # if date_object < today and (length == 5 or length == 6):
            # print day,
            # print ' '.join(game).rjust(30)
            # if date_object > today:
                # break
        
        conn = MySQLConnection(**db_config)
        
        if conn.is_connected():
            cursor = conn.cursor()
            
            add_game = ("REPLACE INTO test "
           "(Day, opponent, homeAway, winLose, score) "
           "VALUES (%(Day)s, %(opponent)s, %(homeAway)s, %(winLose)s, %(score)s);")
           
            data_game = {
                'Day': str(day),
                'opponent': str(opponent),
                'homeAway': str(homeAway),
                'winLose': str(winLose),
                'score': str(score),
            }
            
        cursor.execute(add_game, data_game)
        conn.commit()
        cursor.close()
            
    conn.close()
    print 'Connection Closed'
   
#Add event to calendar   
    with open('client_secrets.json') as file:
        data = json.load(file)
        clientID = data['installed']['client_id']
        clientSecret = data['installed']['client_secret']
        apiKey = data['installed']['api_key']
        Scope = 'https://www.googleapis.com/auth/calendar'
        APPLICATION_NAME = 'Bruins Record'
        calendarId = data['installed']['calendar_id']
        
        FLOW = OAuth2WebServerFlow(client_id = clientID,client_secret = clientSecret, scope=Scope,user_agent='Bruins Record')
        
        storage = Storage('calendar.dat')
        credentials = storage.get()
        if credentials is None or credentials.invalid == True:
            credentials = run_flow(FLOW, storage)
            
        http = httplib2.Http() 
        http = credentials.authorize(http)

        service = build(serviceName='calendar', version='v3', http=http, developerKey=apiKey)
        
        one_day = datetime.timedelta(days=1)
        yesterday = today - one_day
        
        if date_object < today and (length == 5 or length == 6):
            #if there was a game yesterday, create
            result = ' '.join(game)+yesterday+'11:00am-11:05am'
            created_event = service.events().quickAdd(calendarId=calendarId, text = result).execute()
            if date_object > today:
                break

        
        
