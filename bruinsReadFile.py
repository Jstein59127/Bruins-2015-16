import csv
import os
import datetime
import mysql.connector
from mysql.connector import MySQLConnection, Error
from configparser import ConfigParser

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
    today = datetime.datetime.now()
   
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
        
        if date_object < today and (length == 5 or length == 6):
            result = ' '.join(game)
            if date_object > today:
                break
        
        # print day
        # print ' '.join(game).rjust(30)
        # print opponent.ljust(21),        
        # print homeAway.rjust(5),
        # print score,
        # print winLose
        
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
        
# cnx = mysql.connector.connect(user='jstein', password='deffhalen123', database='Bruins2015', host='127.0.0.1')
# cursor = cnx.cursor()


# addGame = ("INSERT INTO test "
           # "(Day, opponent, homeAway, winLose, score) "
           # "VALUES (%(Day)s, %(opponent)s, %(homeAway)s, %(winLose)s, %(score)s);")


# data_game = {
    # 'Day': str(day),
    # 'opponent': str(opponent),
    # 'homeAway': str(homeAway),
    # 'winLose': str(winLose),
    # 'score': str(score),
# }
# while flag:
    # cursor.execute(addGame, data_game)

# cnx.commit()
# cursor.close()
# cnx.close()
   