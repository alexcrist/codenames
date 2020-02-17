from game import Game
from constants import *

game = Game()
players = [RED, BLUE]
turn_index = 0

while True:
    player = players[turn_index]
    game.give_hint(player)
    turn_index = (turn_index + 1) % 2
