from game_shared import *

class GameBase(object):
	def __init__(self, game_screen):
		self.game_screen = game_screen
		self.set_screen_size(1, 1, 1, 1)

		self.tileset_url = None
		self.visible = True
		self.clickable = True
		self.offset = [0,0]

		# Defaults
		self.min_players = 1
		self.max_players = 1
		self.keys_to_request = []
		self.keys_required   = []
		self.keys_pass_on    = False
		self.receive_key_up  = True
		self.timeout = 8 * 60

		self.name = "Game"
		self.instructions = ""
		self.player_slot_names = None # List/tuple of a name for each player slot, in order

	def set_screen_size(self, map_w, map_h, tile_w, tile_h, value = (0,0), over_value = None):
		self.map_w = map_w
		self.map_h = map_h
		self.tile_w = tile_w
		self.tile_h = tile_h
		self.game_map_base = [value]      * (map_w * map_h)
		self.game_map_over = [over_value] * (map_w * map_h)
		self.game_map_changed = True
		self.game_map_config_changed = True

	def set_screen_params(self, tileset_url=None, visible=None, clickable=None, offset=None):
		if tileset_url != None:
			self.tileset_url = tileset_url
		if visible != None:
			self.visible = visible
		if clickable != None:
			self.clickable = clickable
		if offset != None:
			self.offset = offset
		self.game_map_config_changed = True

	def encode_screen(self):
		"""
		The tilemap's data is a list of integers. Formatted like a binary number it would look like:
		  rrrrrrryyyyyyxxxxxx
		  |||||||||||||++++++- X position in the tileset, in tile units
		  |||||||++++++------- Y position in the tileset, in tile units
		  +++++++------------- Number of time to repeat this tile (minus 1)
		"""
		def encode_tile(tile):
			return tile[0] | (tile[1] << 6)

		out = [encode_tile(self.game_map_over[0] or self.game_map_base[0])]
		for tiles in zip(self.game_map_over[1:], self.game_map_base[1:]):
			tile = tiles[0] or tiles[1]
			encoded = encode_tile(tile)
			if (encoded == (out[-1] & 4095)) and (out[-1] < 0b1111111000000000000):
				out[-1] += 4096 # 1 << 12
			else:
				out.append(encoded)
		return out

	# ---------------------------------
	# Helper functions for games to use
	def send_chat(self, text):
		self.game_screen.send_chat(text)

	def tell_user(self, user, text):
		self.game_screen.tell_user(user, text)

	def send_cmd_command(self, command):
		self.game_screen.send_cmd_command(command)

	def set_screen_tile(self, x, y, tile, layer=False):
		map = self.game_map_over if layer else self.game_map_base
		map[y * self.map_w + x] = tile
		self.game_map_changed = True

	def set_screen_tile_rect(self, x, y, w, h, tile, layer=False):
		map = self.game_map_over if layer else self.game_map_base
		for wi in range(w):
			for hi in range(h):
				map[(y+hi) * self.map_w + (x+wi)] = tile
		self.game_map_changed = True

	def get_screen_tile(self, x, y, default=None, layer=False):
		if x < 0 or x >= self.map_w or y < 0 or y >= self.map_h:
			return default
		map = self.game_map_over if layer else self.game_map_base
		return map[y * self.map_w + x]

	def clear_screen(self, tile, layer=False):
		set_screen_tile_rect(0, 0, self.map_w, self.map_h, tile, layer)

	# ---------------------------------------
	# Methods for individual games to override

	def init_game(self):
		pass

	def start_game(self):
		pass

	def stop_game(self):
		pass

	def tick(self):
		pass

	def click(self, player, x, y, map_x, map_y):
		pass

	def key_press(self, player, key):
		pass

	def key_release(self, player, key):
		pass
