from utils import Singleton

class Project(metaclass=Singleton):
    def __init__(self) -> None:
        self.modality = "CT"
        self.window_level = 40
        self.window_width = 350
