from games.game_base import *

class GameConnect4(GameBase):
	def __init__(self, game_screen):
		super().__init__(game_screen)
		self.game_name = "Connect 4"
		self.instructions = "Click on a column to drop a circle in it. You win if you form a line of four circles of your color."
		self.player_slot_names = ("red", "yellow")
		self.min_players = 2
		self.max_players = 2

	def init_game(self):
		self.set_screen_size(3, 3, 16, 16, (1,0))
		self.set_screen_params(tileset_url="https://i.imgur.com/wM3epAe.png", clickable=True)

	def tick(self):
		pass

	def click(self, player, x, y, map_x, map_y):
		at_xy = self.get_screen_tile(map_x, map_y)
		if at_xy == (1,0):
			self.set_screen_tile(map_x, map_y, (2,0))
		else:
			self.set_screen_tile(map_x, map_y, (1,0))

	def key_press(self, player, key):
		print("Key press")

	def key_release(self, player, key):
		print("Key release")
