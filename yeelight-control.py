import logging
import sqlite3
from time import sleep

from yeelight.main import BulbException

from packages.yeecontrol.presets import Preset, PresetExc
from packages.yeecontrol.bulbs import Bulb, BulbExc
from packages.yeecontrol.scenes import Scene, SceneExc

print('\nStarting Yeelight Control . . .')

# config
config_db_path = "yeelight-control.db"
config_log_path = "yeelight-control.log"

# database
conn = sqlite3.connect(config_db_path)
cursor = conn.cursor()

# logger
FORMAT = '%(name)s:%(levelname)s:%(asctime)s:%(message)s'
logging.basicConfig(level=logging.INFO, filename=config_log_path, filemode='a', format=FORMAT)
logger = logging.getLogger()

logger.info('Starting the application')

# init the application
bulbs = Bulb(conn, cursor)
presets = Preset()
scenes = Scene(conn, cursor)

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
            ("\nInvalid input!")
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
                                    bulbs.set(bulb_req, preset)
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
            ("\nInvalid input!")
        else:
            if opt == 1:
                break

def menu_scenes():
    while True:
        print('\nSCENE LIST:')
        try:
            scenes.print_list()
        except SceneExc as e:
            print(e.message)

        print('''
MENU > SCENES:
1. Set scene
2. Add scene
3. Remove scene
4. Export scenes to JSON
5. Import scenes from JSON
6. Back''')
        try:
            opt = int(input(': '))
        except:
            print('\nInvalid input!')
        else:

            if  opt == 1: # set scene
                logger.info('Trying to set a scene ...')
                if len(scenes.list()) == 0:
                    logger.warning('No scenes saved!')
                    print('\nThe scene list is empty!')
                else:
                    try:
                        print('\nEnter a scene name to set:')
                        print('Scenes:', ', '.join(scenes.list()))
                        scene_req = input(': ')
                        scenes.set(scene_req, bulbs, presets)
                    except SceneExc as e:
                        logger.warning(e.message)
                        print(e.message)
                    except:
                        logger.error('Something went wrong while setting a scene')
                        print('Something went wrong!')
                    else:
                        logger.info('Scene ' + scene_req + ' set successfully')

            elif opt == 2: # add scene
                logger.info('Trying to add a new scene ...')
                print('\nEnter a new scene name:')
                name = input(': ')
                print()

                try:
                    scenes.add(name, bulbs, presets)
                except SceneExc as e:
                    logger.warning(e.message)
                    print(e.message)
                except:
                    logger.error('Something went wrong while adding a scene')
                    print('Something went wrong!')
                else:
                    logger.info('Scene ' + name + ' added successfully')

            elif opt == 3: # remove scene
                logger.info('Trying to delete a scene ...')
                if len(scenes.list()) == 0:
                    logger.warning('No scenes to remove!')
                    print('\nNo scenes to remove!')
                else:
                    try:
                        print('\nEnter a scene name to remove:')
                        print('Scenes:', ', '.join(scenes.list()))
                        scene_req = input(': ')
                        scenes.remove(scene_req)
                    except SceneExc as e:
                        logger.warning(e.message)
                        print(e.message)
                    except:
                        logger.error('Something went wrong while removing a scene')
                        print('Something went wrong!')
                    else:
                        logger.info('Bulb ' + scene_req + ' removed successfully')

            elif opt == 4: # export scenes to JSON
                logger.info('Trying to export scenes ...')
                try:
                    scenes.export()
                except SceneExc as e:
                    print()
                    logger.warning(e.message)
                    print(e.message)
                except:
                    logger.error('Something went wrong while exporting scenes')
                    print('\nSomething went wrong!')
                else:
                    logger.info('Scenes exported successfully')
                    print('\nScenes exported successfully.')

            elif opt == 5: # import scenes from JSON
                logger.info('Trying to import scenes from a file ...')
                filename = input('\nEnter file name to import scenes from: ')
                try:
                    scenes.load(filename)
                except FileNotFoundError:
                    logger.warning('No such file: ' + filename)
                    print('File with this name does not exist!')
                except SceneExc as e:
                    logger.warning(e.message)
                    print(e.message)
                except:
                    logger.error('Something went wrong while importing scenes')
                    print('Something went wrong!')

            elif opt == 6:
                break

def menu_ambilight():
    import yeelight
    import time
    from PIL import ImageGrab, ImageStat

    bulb = yeelight.Bulb(bulbs.find_by_name('desk'))
    
    bulb.turn_on
    bulb.effect = 'sudden'
    bulb.start_music()

    try:
        logger.info('Ambient lighting started')
        while True:

            t1 = time.time_ns()

            img = ImageStat.Stat(ImageGrab.grab())
            avg = img.rms

            r = round(avg[0])
            g = round(avg[1])
            b = round(avg[2])

            br = (avg[0] + avg[1] + avg[2]) / 3
            br = round(br * 100 / 255)

            print("Set color:", r, g, b, br, "| Press CTRL+C to stop ambient lighing")
            print(bulb.effect)

            try:
                bulb.set_scene(yeelight.SceneClass.COLOR, r, g, b, br / 2)
            except:
                logger.info('An error while running ambi light')
                print('An error occurred')

            t2 = time.time_ns()

            print("Frame processing time:", (t2 - t1) / 1000000, "ms")

            sleep(0.4)

    except KeyboardInterrupt:
        logger.info('Ambient lighting ended')
        print('Ambient lighting ended.')

        bulbs.set('desk', presets.get('warm'))


# main menu
try:
    while True:
        print('''
MENU:
1. Bulbs
2. Presets
3. Scenes
4. Ambient Light
5. Exit''')
        try:
            opt = int(input(': '))
        except:
            ("\nInvalid input!")
        else:

            if opt == 1:
                menu_bulbs()

            elif opt == 2:
                menu_presets()

            elif opt == 3:
                menu_scenes()

            elif opt == 4:
                menu_ambilight()

            elif opt == 5:
                raise KeyboardInterrupt
except KeyboardInterrupt:
    print("\nClosing the application . . . \n")
    conn.close()
    logger.info('Closing the application')

sleep(2)
