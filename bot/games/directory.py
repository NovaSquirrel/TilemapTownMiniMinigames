from games.game_connect4 import GameConnect4, GameConnect4Big
from games.game_bubblepop import GameBubblePop, GameBubblePopSquare, GameBubblePopMax, GameBubblePopMultiplayer, GameBubblePopSameGame, GameBubblePopSameGameExtended
from games.game_reversi import GameReversi, GameReversiBig

game_directory = {}
game_directory['connect_4'] = GameConnect4
game_directory['connect_4_big'] = GameConnect4Big
game_directory['bubblepop'] = GameBubblePop
game_directory['bubblepop_square'] = GameBubblePopSquare
game_directory['bubblepop_max'] = GameBubblePopMax
game_directory['bubblepop_multi'] = GameBubblePopMultiplayer
game_directory['samegame'] = GameBubblePopSameGame
game_directory['samegame_extend'] = GameBubblePopSameGameExtended
game_directory['reversi'] = GameReversi
game_directory['reversi_big'] = GameReversiBig
