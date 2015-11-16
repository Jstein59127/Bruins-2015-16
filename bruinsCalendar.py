import json
import httplib2
from apiclient import discovery
from oauth2client import client
from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run_flow
import datetime
with open('client_secrets.json') as file:
    data = json.load(file)
    clientID = data['installed']['client_id']
    clientSecret = data['installed']['client_secret']
    apiKey = data['installed']['api_key']
    Scope = 'https://www.googleapis.com/auth/calendar'
    APPLICATION_NAME = 'Bruins Record'
    calendarId = data['installed']['calendar_id']
   
    FLOW = OAuth2WebServerFlow(client_id = clientID,client_secret = clientSecret, scope=Scope,user_agent='Bruins Record')
    awayScore = 'Bruins 4 - '
    homeScore = 'Montreal 1 9:53am-9:54am'
    result = '%s%s' % (awayScore, homeScore)

    storage = Storage('calendar.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid == True:
        credentials = run_flow(FLOW, storage)
        
    http = httplib2.Http() 
    http = credentials.authorize(http)
    
    service = build(serviceName='calendar', version='v3', http=http, developerKey=apiKey)
   
        
    if date_object < today and (length == 5 or length == 6):
        #if there was a game yesterday, create
        result = ' '.join(game)+yesterday+'11:00am-11:05am'
        created_event = service.events().quickAdd(calendarId=calendarId, text = result).execute()
        if date_object > today:
            break

    created_event = service.events().quickAdd(calendarId=calendarId, text = result).execute() 
    