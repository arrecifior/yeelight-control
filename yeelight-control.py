import logging
import configparser
import sqlite3

from packages.yeecontrol.presets import Preset, PresetExc
from packages.yeecontrol.bulbs import Bulb, BulbExc
from packages.yeecontrol.scenes import Scene, SceneExc

print('\nStarting Yeelight Control . . .')

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

logger.info('Starting the application')

# init the application
bulbs = Bulb(conn, cursor)
presets = Preset()
#scenes = Scene(conn, cursor)

# menu

def menu_bulbs():
    while True:

        # list of all bulbs
        print('\nBULBS LIST:')
        try:
            logger.info('Trying to print bulb list ...')
            bulbs.print_list()
        except BulbExc as e:
            logger.warning(e.message)
            print(e.message)
        except:
            logger.warning('Something went wrong while printing bulb list')
            print('Something went wrong while printing bulb list')
        else:
            logger.info('Bulb list printed successfully')

        print('''
MENU > BULBS:
1. Refresh
2. Set bulb state
3. Add bulbs
4. Remove a bulb
5. Back''')
        try:
            opt = int(input(': '))
        except:
            ("\nInvalid input!\n")
        else:

            if opt == 1: # refresh bulbs list
                continue

            elif opt == 2: # set bulb to a preset
                logger.info('Trying to set a bulb to a preset ...')
                if len(bulbs.list()) == 0:
                    logger.warning('No bulbs to set!')
                    print('\nNo bulbs to set!')
                else:
                    while True:
                        print('\nEnter a preset name from the list (enter \'back\' to cancel):')
                        print('Presets:', ', '.join(presets.list()))
                        try:
                            preset_req = input(': ')
                            if preset_req == 'back':
                                break
                            preset = presets.get(preset_req)
                        except PresetExc as e:
                            logger.warning(e.message)
                            print(e.message)
                        except:
                            logger.error('Something went wrong!')
                            print('Something went wrong!')
                        else:
                            while True:
                                print('\nEnter a bulb name from the list (enter \'back\' to cancel):')
                                print('Bulbs:', ', '.join(bulbs.list()))
                                try:
                                    bulb_req = input(': ')
                                    if bulb_req == 'back':
                                        break
                                    bulbs.set_bulb(bulb_req, preset)
                                except BulbExc as e:
                                    logger.warning(e.message)
                                    print(e.message)
                                except:
                                    logger.error('Something went wrong!')
                                    print('Something went wrong!')
                                else:
                                    logger.info('Bulb ' + bulb_req + ' set to preset' + preset_req)
                                    break
                            break

            elif opt == 3:
                try:
                    print()
                    logger.info('Trying to add bulbs ...')
                    bulbs.add()
                except BulbExc as e:
                    logger.warning(e.message)
                    print(e.message)
                except:
                    logger.warning('Something went wrong while adding bulbs')
                    print('Something went wrong!')
                else:
                    logger.info('Bulb adding process finished successfully')

            elif opt == 4:
                logger.info('Trying to delete a bulb ...')
                if len(bulbs.list()) == 0:
                    logger.warning('No bulbs to remove!')
                    print('\nNo bulbs to remove!')
                else:
                    try:
                        print('\nEnter a bulb name to remove:')
                        print('Bulbs:', ', '.join(bulbs.list()))
                        bulb_req = input(': ')
                        bulbs.remove(bulb_req)
                    except BulbExc as e:
                        logger.warning(e.message)
                        print(e.message)
                    except:
                        logger.error('Something went wrong while removing a bulb')
                        print('Something went wrong!')
                    else:
                        logger.info('Bulb ' + bulb_req + ' removed successfully')

            elif opt == 5:
                break

def menu_presets():
    while True:
        print('\nPRESETS LIST:')
        print('', ', '.join(presets.list()))

        print('''
MENU > PRESETS:
1. Back''')
        try:
            opt = int(input(': '))
        except:
            ("\nInvalid input!\n")
        else:
            if opt == 1:
                break


def menu_scenes():
    print('\nFeature unavailable!')

# main menu
while True:
    print('''
MENU:
1. Bulbs
2. Presets
3. Scenes
4. Exit''')
    try:
        opt = int(input(': '))
    except:
        ("\nInvalid input!\n")
    else:

        if opt == 1:
            menu_bulbs()

        elif opt == 2:
            menu_presets()

        elif opt == 3:
            menu_scenes()

        elif opt == 4:
            print("\nClosing the application . . . \n")
            conn.close()
            logger.info('Closing the application')
            break
    