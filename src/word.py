from text_formatters import pad, gray
from text_formatters import colorizer_map

class Word():
    ''' A word in Codenames '''

    def __init__(self, string, color):
        self.string = string
        self.color = color
        self.has_been_guessed = False

    def __str__(self):
        padded_string = pad(self.string)
        colorizer = gray
        if self.has_been_guessed:
            colorizer = colorizer_map[self.color]
        return colorizer(padded_string)

    def set_to_guessed(self):
        self.has_been_guessed = True
