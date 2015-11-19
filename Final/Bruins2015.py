#Script to pull the full schedule.csv from the Bruins website, adds the game information (Day, Opponent, Home or Away, Win or Lose, and Score) to a MySQL database, as well as adding game information (Result of Game, Day, and Time) to a Google calendar.  Uses Windows Task Scheduler to run every day at a certain time

#Written on Windows

#Author: Jimmy Stein

#Notes:
#If adding to MySQL database, MySQL connector for Python must be installed.
#pip install --upgrade google-api-python-client
#pip install configparser
#MySQL table information: 
    #Day - type DATE
    #opponent - type VARCHAR(50)
    #homeAway - type VARCHAR(5)
    #winLose - type VARCHAR(4)
    #score - type VARCHAR(10) - in case for some reason the score is huge
#See client_secrets.json and config.ini for configuration - edit as needed
#api key is found in Google's Developer Console
    # http://console.developers.google.com
    # Credentials
    # Add credentials, choose the type, and download the client_secrets.json file specific to the project
#calendarId is found on https://calendar.google.com
    #Click on the arrow next to the calendar and hit Calendar Settings, calendar ID is displayed in the Calendar Address row

#Built in modules
import sys
import os 
import datetime
import csv
import httplib2
import urllib
import json

#External Modules
import mysql.connector
from mysql.connector import MySQLConnection, Error
from apiclient import discovery
from oauth2client import client
from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run_flow
from configparser import ConfigParser

today = datetime.datetime.now()
tomorrow = today + datetime.timedelta(days=1)

#Download File
def download_file():
    BruinsPath = r'C:\Programming\Bruins2015\Final'
    os.chdir(BruinsPath)
    url = 'http://bruins.nhl.com/schedule/full.csv'
    schedule = urllib.URLopener()
    schedule.retrieve(url, "schedule.csv")

#Reads Configuration file.  File contains MySQL Database information
def read_config(filename, section):
    parser = ConfigParser()
    parser.read(filename)
    store = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            store[item[0]] = item[1]
    else:
        raise Exception('{0} not found in the{1} file'.format(section, filename))
    
    return store
        
download_file()  

bruins = open('schedule.csv', 'r')

#File needed to access Google Calendar using Google's API
file = open('client_secrets.json')

#Temporary file to store game information for adding an event in the calendar
text = open('Games.txt', 'w+')

#Loads Google Calendar API Information
#Note: api key and calendar id are not originally in the client_secrets.json file.  They were added for security and convenience.
data = json.load(file)
clientID = data['installed']['client_id']
clientSecret = data['installed']['client_secret']
apiKey = data['installed']['api_key']
Scope = 'https://www.googleapis.com/auth/calendar'
APPLICATION_NAME = 'Bruins Record'
calendarId = data['installed']['calendar_id']
        
FLOW = OAuth2WebServerFlow(client_id = clientID,client_secret = clientSecret, scope=Scope,user_agent='Bruins Record')

#Stores calendar data in external .dat file
storage = Storage('calendar.dat')

credentials = storage.get()
if credentials is None or credentials.invalid == True:
    credentials = run_flow(FLOW, storage)
            
http = httplib2.Http() 
http = credentials.authorize(http)

service = build(serviceName='calendar', version='v3', http=http, developerKey=apiKey)

db_config = read_config('config.ini', 'mysql')
homeAway = ''
opponent = ''

read_file = csv.reader(bruins)
text = open('Games.txt', 'w+')

#Reads in file and extracts the day played and the game
#Formats the file to add to database, as well writes Google-Calendar-Formatted strings to 'Games.txt'
for line in read_file:
    
    #Skips headers and pre-season games - will have to update yearly for new schedule
    if line[0] == 'START_DATE' or line[0] == '09/20/2015' or line[0] == '09/22/2015' or line[0] == '09/24/2015' or line[0] == '09/26/2015' or line[0] == '09/28/2015' or line[0] == '09/30/2015' or line[0] == '10/02/2015':
        continue

    day_played = line[0]
    date_object = datetime.datetime.strptime(day_played, "%m/%d/%Y")
    day = date_object.strftime("%Y%m%d")
    game = line[3].split()
    length = len(game)
    calendar_date_object = datetime.datetime.strptime(day_played, "%m/%d/%Y")
    calendar_day = calendar_date_object.strftime("%B %d %Y")

    if date_object < today and (length == 5 or length == 6):
        result = line[3] + ' on ' + calendar_day + ' 11:00-11:05am'
        json.dump(result, text)  
        text.write('\n')
        #For testing purposes: 
            #To add all the events to the calendar instead of the last one:
        # service.events().quickAdd(calendarId=calendarId, text = result).execute()
    
    if game[0] == 'Boston':
        homeAway = 'Away'
    else:
        homeAway = 'Home'
        
    #When inserting data to MySQL database, score always has the larger number on the left
    if homeAway == 'Away':
        if length == 3:
            opponent = game[2]
            score = ''
            winLose = ''
        elif length == 4:
            opponent = game[2] + game[3]
            score = '' 
            winLose = ''
        elif length == 5:
            opponent = game[3]
            if game[1] > game[4]:
                winLose = 'Win'
                score = game[1] + game[2] + game[4]
            else:
                winLose = 'Lose'
                score = game[4] + game[2] + game[1]
        elif length == 6:
            opponent = game[3] + game[4]
            if game[1] > game[5]:
                winLose = 'Win'
                score = game[1] + game[2] + game[5]
            else:
                winLose = 'Lose'
                score = game[5] + game[2] + game[1]
    else:
        if length == 3:
            opponent = game[0]
            score = ''
            winLose = ''
        elif length == 4:
            opponent = game[0] + game[1]
            score = ''
            winLose = ''
        elif length == 5:
            opponent = game[0]
            if game[1] > game[4]:
                winLose = 'Lose'
                score = game[1] + game[2] + game[4]
            else:
                winLose = 'Win'
                score = game[4] + game[2] + game[1]
        elif length == 6:
            opponent = game[0] + game[1]
            if game[2] > game[5]:
                winLose = 'Lose'
                score = game[2] + game[3] + game[5]
            else:
                winLose = 'Win'
                score = game[5] + game[3] + game[2]
    
    #Schedule consists of abbreviated team name.  This is will convert the name to the actual team name
    opponentDict = {
    'Montreal':'Montreal Canadiens',
    'Winnipeg':'Winnipeg Jets',
    'Dallas':'Dallas Stars',
    'NyRangers':'New York Rangers',
    'StLouis':'St. Louis Blues',
    'NyIslanders':'New York Islanders',
    'Washington':'Washington Capitals',
    'Minnesota':'Minnesota Wild',
    'Nashville':'Nashville Predators',
    'LosAngeles':'Los Angeles Kings',
    'Vancouver':'Vancouver Canucks',
    'Pittsburgh':'Pittsburgh Penguins',
    'Chicago':'Chicago Blackhawks',
    'Ottawa':'Ottawa Senators',
    'TampaBay':'Tampa Bay Lightning',
    'Detroit':'Detroit Red Wings',
    'NewJersey':'New Jersey Devils',
    'Florida':'Florida Panthers',
    'SanJose':'San Jose Sharks',
    'Arizona':'Arizona Coyotes',
    'Carolina':'Carolina Hurricanes',
    'Buffalo':'Buffalo Sabres',
    'Philadelphia':'Philadelphia Flyers',
    'Edmonton':'Edmonton Oilers',
    'Colorado':'Colorado Avalanche',
    'Calgary':'Calgary Flames',
    'Toronto':'Toronto Maple Leafs',
    'Anaheim':'Anaheim Ducks',
    'Columbus':'Columbus Blue Jackets'}
    
    if opponent in opponentDict:
        opponent = opponentDict[opponent]
        
    #Connects to MySQL database using external file
    conn = MySQLConnection(**db_config)
        
    if conn.is_connected():
        cursor = conn.cursor()
        
        #Overwrites existing entries in table - if overwriting is not desired, use "INSERT INTO"
        add_game = ("REPLACE INTO record "
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
    
    if date_object > today:
        break
        
text.close()
with open('Games.txt') as g:
    data = []
    for dataLine in g:
        convert = unicode(dataLine)
        data.append(json.loads(convert))
    
    #Prevents duplicate calendar entries
    if tomorrow > date_object:
        service.events().quickAdd(calendarId=calendarId, text = data[-1]).execute()
    else:
        sys.exit('Game Already In Calendar, Exiting...')
   
file.close()
bruins.close()
print 'Connection Closed'