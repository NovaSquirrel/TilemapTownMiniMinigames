from games.base import *
from games.tilesets import *

class GameDemo(GameBase):
	name = "Demo"
	instructions = "Test instructions"
	player_slot_names = ("red", "yellow")
	min_players = 2
	max_players = 2
	keys_to_request = ["move-n", "move-ne", "move-e", "move-se", "move-s", "move-sw", "move-w", "move-nw"]
	keys_required   = ["move-n", "move-ne", "move-e", "move-se", "move-s", "move-sw", "move-w", "move-nw"]

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
