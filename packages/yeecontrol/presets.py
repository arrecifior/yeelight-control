class PresetExc(Exception):
    """Generic exception for Preset class."""
    def __init__(self, message, head="PresetException", ):
        super().__init__(message)
        self.head = head
        self.message = message

class Preset():
    """A class to represent a list of presets.
    
    Attributes:
    -----------
    __list: dict
        Stores presets data as a dict of dict's

    Methods:
    --------
    get(name)
        Return preset data by name.
    list()
        Return a list of all presets names.
    """

    __list = {
        'off': {'brightness': 0},
        'dim': {'brightness': 1, 'mode': 'CT', 'value': 1700},
        'warm': {'brightness': 100, 'mode': 'CT', 'value': 2700},
        'neutral': {'brightness': 100, 'mode': 'CT', 'value': 3200},
        'cold': {'brightness': 100, 'mode': 'CT', 'value': 5000},
        'red': {'brightness': 100, 'mode': 'RGB', 'value': [255, 0, 0]},
        'green': {'brightness': 100, 'mode': 'RGB', 'value': [0, 255, 0]},
        'blue': {'brightness': 100, 'mode': 'RGB', 'value': [0, 0, 255]},
        'red_dim': {'brightness': 1, 'mode': 'RGB', 'value': [255, 0, 0]}
        }

    def get(self, name: str) -> dict:
        """Returns a dictionary with preset data.
        
        Parameters:
        -----------
        name: str
            Name of a preset
        """
        
        if name not in self.__list.keys():
            raise PresetExc('No preset with such name: ' + name)
        else:
            return self.__list.get(name)

    def list(self) -> list:
        """Returns preset list."""

        presets = []
        for preset in self.__list.keys():
            presets.append(preset)
        return presets
