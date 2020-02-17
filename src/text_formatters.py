from constants import *

# Color a string
def paint(text, colorNum):
    return "\x1b[{}m{}\x1b[0m".format(colorNum, text)

red = lambda text: paint(text, 91)
blue = lambda text: paint(text, 94)
green = lambda text: paint(text, 92)
black = lambda text: text
gray = lambda text: paint(text, 37)

colorizer_map = {
    RED: red,
    BLUE: blue,
    GREEN: green,
    BLACK: black
}

# Pad a string to character width
pad = lambda word: word + (" " * (WORD_WIDTH - len(word)))
