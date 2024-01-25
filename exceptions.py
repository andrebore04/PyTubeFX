from pytubefix.colors import Color

class PytubeGUIException(Exception):
    """Base exception class for all pytubeGUI exceptions to inherit"""


class InvalidInput(PytubeGUIException):
    """Invalid input, either too short or not valid for pytubefix"""
    def __init__(self, user_input: str, error_info: str):
        self.user_input = user_input
        self.error_info = error_info
        
        super().__init__(user_input)

    @property
    def error_string(self):
        return f'Input is invalid: {self.error_info}'

    @property
    def error_string_color(self):
        return Color.RED + self.error_string + Color.RESET


class ThumbnailNotFound(PytubeGUIException):
    """Thumbnail failed to load, video should be ok"""
    def __init__(self, video_id: str):
        self.video_id = video_id
        
        super().__init__(video_id)

    @property
    def error_string(self):
        return f'Thumbnail could not be loaded, but video should be ok.'

    @property
    def error_string_color(self):
        return Color.RED + self.error_string + Color.RESET