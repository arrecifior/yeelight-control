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

    def __find_by_ip(self, ip): # find the bulb by ip, return name
        found = False
        
        for bulb in self.__cursor.execute('SELECT name, ip FROM bulbs;'):
            if bulb[1] == ip:
                found = True
                return bulb[0]

        if not found:
            return None

    def __find_by_name(self, name): # find the bulb by name, return ip
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

    def list(self): # returns list of bulb names
        bulbs = []
        for bulb in self.__cursor.execute('SELECT name FROM bulbs;'):
            bulbs.append(bulb[0])
        return bulbs

    def print_list(self): # prints all bulbs
        if len(self.list()) == 0:
            raise BulbExc('No bulbs saved.')  
        for bulb in self.__cursor.execute('SELECT name, ip FROM bulbs;'):
            print('{0:<15}{1:<10}{2:<11}'.format(bulb[1], bulb[0], self.__status(bulb[0])))      

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

    def set(self, name, preset): # se bulb to a preset:
        if self.__status(name) == None:
            raise BulbExc('No bulb with such name: ' + name)

        b = yeelight.Bulb(self.__find_by_name(name))

        if preset.get('brightness') == 0:
            b.turn_off()
        else:
            b.set_brightness(preset.get('brightness'))
            if preset.get('mode') == 'CT': 
                b.set_color_temp(degrees=preset.get('value'))
            elif preset.get('mode') == 'RGB':
                b.set_rgb(red=preset.get('value')[0], green=preset.get('value')[1], blue=preset.get('value')[2])
            b.turn_on()
