import yeelight

class SceneExc(Exception): # generic scene exception
    def __init__(self, message, head="SceneException", ):
        super().__init__(message)
        self.head = head
        self.message = message

class Scene():
    def __init__(self, conn, cursor):
        self.__cursor = cursor
        self.__conn = conn
        # create db table if not exitsts
        self.__cursor.execute('''CREATE TABLE IF NOT EXISTS scenes (
                    name TEXT PRIMARY KEY,
                    settings TEXT NOT NULL
                    );''')

    def __find(self, name): # returns False if scene with said name does not exist
        found = False
        for scene in self.__cursor.execute('SELECT name, values FROM scenes;'):
            if scene[0] == name:
                found = True
        return found

    def list(self): # returns a list of all scenes
        scenes = []
        for scene in self.__cursor.execute('SELECT name FROM scenes;'):
            scenes.append(scene[0])
        return scenes

    def print_list(self): # print formatted list of all
        if len(self.list()) == 0:
            raise SceneExc('No scenes saved.')
        for scene in self.__cursor.execute('SELECT name, settings FROM scenes;'):
            print('{0:<15}'.format(scene[0] + ':'), end='')
            settings = scene[1].split(';')
            for item in range(len(settings) - 1):
                if not item % 2:
                    print('  ', settings[item], ':', settings[item + 1], end='')
            print()

    def add(self, name, bulbs, presets): # add a new scene
        settings = []
        if len(bulbs.list()) == 0:
            raise SceneExc('No bulbs to add to a scene')
        if name in self.list():
            raise SceneExc('Scene with this name already exists: ' + name)
       
        for bulb in bulbs.list():
            while True:
                print(bulb, ': choose a scene for the bulb. Press Enter to skip.')
                print('Presets:', ', '.join(presets.list()))
                preset_req = input(': ')

                if preset_req in presets.list():
                    settings.append(bulb)
                    settings.append(preset_req)
                    break
                elif preset_req == '':
                    break
                else:
                    print('\nInvalid input!')

            print()

        if len(settings) == 0:
            raise SceneExc('Cannot save an empty scene!')

        self.__cursor.execute('INSERT INTO scenes (name, settings) VALUES (?,?)', (name, ';'.join(settings)))
        self.__conn.commit()

    def remove(self, name): # remove a scene
        if name not in self.list():
            raise SceneExc('No scene with such name: ' + name)
        else:
            self.__cursor.execute('DELETE FROM scenes WHERE name = ?;', (name,))
            self.__conn.commit()

    def set(self, name, bulbs, presets): # set bulbs to a scene states
        if len(self.list()) == 0:
            raise SceneExc('No scenes saved!')
        if name not in self.list():
            raise SceneExc('No scene with such name: ' + name)
        
        unavailable = False

        for scene in self.__cursor.execute('SELECT name, settings FROM scenes;'):
            if scene[0] == name:
                settings = scene[1].split(';')
                for item in range(len(settings) - 1):
                    if not item % 2:
                        try:
                            bulbs.set(settings[item], presets.get(settings[item + 1]))
                        except yeelight.main.BulbException:
                            unavailable = True

        if unavailable:
            raise SceneExc('Some bulbs were unavailable.')
