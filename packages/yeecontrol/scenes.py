class SceneExc(Exception): # generic scene exception
    def __init__(self, message, head="SceneException", ):
        super().__init__(message)
        self.head = head
        self.message = message

class Scene():
    pass