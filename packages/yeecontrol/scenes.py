import json
import yeelight

class SceneExc(Exception):
    """Generic exception for the Scene class."""
    def __init__(self, message, head="SceneException", ):
        super().__init__(message)
        self.head = head
        self.message = message

class Scene():
    """A class to repesent a list of lighting scenes.

    Methods:
    --------

    list()
        Returns a list of scene names.
    print_list()
        Prints a formatted list of scenes.
    add(name, bulbs, presets)
        Adds a new preset.
    remove(name)
        Removes a named preset
    set(name, bulbs, presets)
        Sets bulbs to a named preset.
    export()
        Exports scenes to a JSON file.
    load(filename)
        Imports scenes from a JSON file.
    """

    def __init__(self, conn, cursor):
        """
        Parameters:
        ----------
        conn:
            Connection object for SQLite connection.
        cursor:
            Cursor object for SQLite connection.
        """

        self.__cursor = cursor
        self.__conn = conn
        # create db table if not exitsts
        self.__cursor.execute('''CREATE TABLE IF NOT EXISTS scenes (
                    name TEXT PRIMARY KEY,
                    settings TEXT NOT NULL
                    );''')

    def list(self) -> list:
        """Returns a list of all scene names."""

        scenes = []
        for scene in self.__cursor.execute('SELECT name FROM scenes;'):
            scenes.append(scene[0])
        return scenes

    def print_list(self):
        """Prints a formatted list of all scenes."""

        if len(self.list()) == 0:
            raise SceneExc('No scenes saved.')
        for scene in self.__cursor.execute('SELECT name, settings FROM scenes;'):
            print('{0:<15}'.format(scene[0] + ':'), end='')
            settings = json.loads(scene[1])
            for bulb in settings.keys():
                print('  ', bulb, ':', settings.get(bulb), end='')
            print()

    #TODO change settings sctructure saved into the DB : affects print_list() and set()
    def add(self, name: str, bulbs: object, presets: object):
        """Adds a new scene.

        Parameters:
        -----------
        name:
            Name of a new preset.
        bulbs:
            Bulb class object to acces bulb interactions.
        presets:
            Preset class to access presets.
        """

        settings = {}
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
                    settings.update({bulb: preset_req})
                    break
                elif preset_req == '':
                    break
                else:
                    print('\nInvalid input!')

            print()

        if len(settings.keys()) == 0:
            raise SceneExc('Cannot save an empty scene!')

        self.__cursor.execute('INSERT INTO scenes (name, settings) VALUES (?,?)', (name, json.dumps(settings)))
        self.__conn.commit()

    def remove(self, name: str):
        """Removes a scene.
        
        Parameters:
        -----------
        name
            Name of the scene.
        """

        if name not in self.list():
            raise SceneExc('No scene with such name: ' + name)
        else:
            self.__cursor.execute('DELETE FROM scenes WHERE name = ?;', (name,))
            self.__conn.commit()

    def set(self, name: str, bulbs: object, presets: object):
        """Sets bulbs to a named preset.

        Parameters:
        -----------
        name
            Name of the scene to set.
        bulbs
            Bulb class object.
        presets
            Preset class object.
        """

        if len(self.list()) == 0:
            raise SceneExc('No scenes saved!')
        if name not in self.list():
            raise SceneExc('No scene with such name: ' + name)
        
        unavailable = False

        for scene in self.__cursor.execute('SELECT name, settings FROM scenes;'):
            if scene[0] == name:
                settings = json.loads(scene[1])
                for bulb in settings.keys():
                    try:
                        bulbs.set(bulb, presets.get(settings.get(bulb)))
                    except yeelight.main.BulbException:
                        unavailable = True

        if unavailable:
            raise SceneExc('Some bulbs were unavailable.')

    def export(self):
        """Exports all saved scenes to a scenes-export.json file."""

        if len(self.list()) == 0: # checking if there are any scenes
            raise SceneExc('No scenes to export!')
        scenes = {}
        for scene in self.__cursor.execute('SELECT name, settings FROM scenes;'):
            settings = json.loads(scene[1])
            scenes.update({scene[0]: settings})

        with open('scenes-export.json', 'w') as outfile: # saving scenes to JSON
            json.dump(scenes, outfile, sort_keys=True, indent=4)

    def load(self, filename):
        """Imports scenes from a JSON file.

        Parameters:
        -----------
        filename
            Name of a file to import scenes from.
        """

        with open(filename, 'r') as infile: 
            try: # checking if a file is a valid json
                scenes = json.load(infile)
            except json.JSONDecodeError:
                raise SceneExc('Corrupted data in file: ' + filename)

        found_empty = False
        found_duplicate = False
        scenes_added = 0

        for scene in scenes.keys():
            if len (scenes.get(scene).keys()) == 0:
                found_empty = False
                continue # skip if settings are empty
            if scene in self.list():
                found_duplicate = True
                continue # skip if preset is already on the list

            self.__cursor.execute('INSERT INTO scenes (name, settings) VALUES (?,?)', (scene, json.dumps(scenes.get(scene))))
            self.__conn.commit()
            scenes_added += 1

        if found_empty or found_duplicate or scenes_added == 0:
            message = ''
            
            if scenes_added == 0:
                message += 'No new scenes added. '
            if found_empty:
                message += 'Skipped empty scene(s). '
            if found_duplicate:
                message += 'Skipped duplicate(s). '

            raise SceneExc(message)
