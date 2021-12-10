import logging
import configparser
import sqlite3

import yeelight
import yeelight.transitions as yeensitions

class BulbExc(Exception): # generic bulb exception
    def __init__(self, message, head="BulbException", ):
        super().__init__(message)
        self.head = head
        self.message = message

class Bulb():
    def __init__(self, conn, cursor):
        self.__cursor = cursor
        self.__conn = conn
        # create db table if not exists
        self.__cursor.execute('''CREATE TABLE IF NOT EXISTS bulbs (
                    name TEXT PRIMARY KEY,
                    ip TEXT NOT NULL
                    );''')

    # setting up bulb indication pattern
    __flash = yeelight.Flow(
        count = 100,
        transitions = yeensitions.alarm()
    )

    def __find_by_ip(self, ip): # find the bulb by ip
        found = False
        
        for bulb in self.__cursor.execute('SELECT name, ip FROM bulbs;'):
            if bulb[1] == ip:
                found = True
                return bulb[0]

        if not found:
            return None

    def __find_by_name(self, name): # find the bulb by name
        found = False
        
        for bulb in self.__cursor.execute('SELECT name, ip FROM bulbs;'):
            if bulb[0] == name:
                found = True
                return bulb[1]

        if not found:
            return None

    def __status(self, name): # checking status of a lightbulb
        found = False
        
        for bulb in self.__cursor.execute('SELECT name, ip FROM bulbs;'):
            if bulb[0] == name:
                found = True
                b = yeelight.Bulb(bulb[1])
                try:
                    return b.get_properties().get('power')
                except:
                    return 'unavailable'

        if not found:
            return None

    def print_list(self): # print all bulbs
        bulbs_count = 0
        for bulb in self.__cursor.execute('SELECT name, ip FROM bulbs;'):
            bulbs_count += 1
            b = yeelight.Bulb(bulb[1])
            print('{0:<15}{1:<10}{2:<11}'.format(bulb[1], bulb[0], self.__status(bulb[0])))
        if bulbs_count == 0:
            raise BulbExc('No bulbs listed!')    

    def add(self): # adding new bulbs
        print('Searching for bulbs . . .')
        # getting bulbs list
        res = yeelight.discover_bulbs()

        if len(res) == 0: # check if any bulbs are online
            raise BulbExc('No bulbs are discoverable')
        new_bulbs = 0
        print('Bulbs found:', len(res))
        for bulb in res:

            # skip if the bulb is already in the DB
            if self.__find_by_ip(bulb.get('ip')) != None:
                continue

            new_bulbs += 1 # counting bulbs available and not in database

            # assign temporary bulb object
            b = yeelight.Bulb(bulb.get('ip'))

            # physical bulb indication
            b.turn_on()
            b.start_flow(self.__flash)

            print('Bulb found at IP:', bulb.get('ip'))

            # adding bulb to the database
            while True:
                name = input("Enter bulb name (press Enter to skip): ")
                if name == "":
                    break
                elif self.__find_by_name(name) == None:
                    self.__cursor.execute('INSERT INTO bulbs (name, ip) VALUES (?,?)', (name, bulb.get('ip')))
                    self.__conn.commit()
                    print("Bulb", name, "has been added.")
                    break
                else:
                    print("Bulb with this name already exists!")
            
            b.stop_flow()

        if new_bulbs == 0:
            raise BulbExc('No bulbs to add!')
        print('No more bulbs to add.')

    def remove(self, name): # delete a bulb
        if self.__status(name) == None:
            raise BulbExc("No bulb with such name: " + name)
        else:
            self.__cursor.execute('DELETE FROM bulbs WHERE name = ?;', (name,))
            self.__conn.commit()

    def set_bulb(self, name, preset):
        b = yeelight.Bulb(self.__find_by_name(name))
        print(b.get_properties())

        if preset.get('brightness') == 0:
            b.turn_off()
        else:
            b.set_brightness(preset.get('brightness'))
            if preset.get('mode') == 'CT': 
                b.set_color_temp(degrees=preset.get('value'))
            elif preset.get('mode') == 'RGB':
                b.set_rgb(red=preset.get('value')[0], green=preset.get('value')[1], blue=preset.get('value')[2])
            b.turn_on()

class PresetExc(Exception): # generic preset exception
    def __init__(self, message, head="PresetException", ):
        super().__init__(message)
        self.head = head
        self.message = message

class Preset():
    __list = {
        'off': {'brightness': 0},
        'dim': {'brightness': 1, 'mode': 'CT', 'value': 1700},
        'warm': {'brightness': 100, 'mode': 'CT', 'value': 2700},
        'neutral': {'brightness': 100, 'mode': 'CT', 'value': 3200},
        'cold': {'brightness': 100, 'mode': 'CT', 'value': 5000},
        'red': {'brightness': 100, 'mode': 'RGB', 'value': [255, 0, 0]},
        'green': {'brightness': 100, 'mode': 'RGB', 'value': [0, 255, 0]},
        'blue': {'brightness': 100, 'mode': 'RGB', 'value': [0, 255, 0]},
        'red_dim': {'brightness': 1, 'mode': 'RGB', 'value': [255, 0, 0]}
        }

    def get(self, name):
        if name not in self.__list.keys():
            raise PresetExc('No preset with such name: ' + name)
        else:
            return self.__list.get(name)

# housekeeping

# config
config = configparser.ConfigParser()
config.read('config.ini')

# database
conn = sqlite3.connect(config.get('DEFAULT', 'db-path'))
cursor = conn.cursor()

# logger
FORMAT = '%(name)s:%(levelname)s:%(asctime)s:%(message)s'
logging.basicConfig(level=logging.INFO, filename=config.get('DEFAULT', 'log-file'), filemode='a', format=FORMAT)
logger = logging.getLogger()

# menu logic
logger.info('Staring the application')

bulbs = Bulb(conn, cursor)

# adding lightbulbs
try:
    logger.info('Trying to add bulbs')
    bulbs.add()
except BulbExc as e:
    logger.warning(e.message)
    print(e.message)
except:
    logger.warning('Something went wrong while adding bulbs')
    print('Something went wrong!')
else:
    logger.info('Bulb adding pricess finished successfully')

# list of all bulbs
try:
    logger.info('Trying to print bulb list')
    bulbs.print_list()
except BulbExc as e:
    logger.warning(e.message)
    print(e.message)
except:
    logger.warning('Something went wrong while printing bulb list')
    print('Something went wrong!')
else:
    logger.info('Bulb list printed successfully')

bulbs.set_bulb('desk', Preset().get('sus'))

conn.close()

logger.info('Closing the application')
    