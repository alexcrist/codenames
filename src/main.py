from game import Game
from constants import *
from text_formatters import colorizer_map

while True:
    game = Game()
    players = [RED, BLUE]
    turn_index = 0

    while True:
        player = players[turn_index]
        winner = game.give_hint(player)

        if winner != False:
            colorize = colorizer_map[winner]
            print(colorize(f"{winner.upper()} WINS!\n\n"))
            break

        turn_index = (turn_index + 1) % 2
