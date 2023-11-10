from games.base import *
from games.tilesets import *
import random

class GameConnect4(GameBase):
	def __init__(self, game_screen):
		super().__init__(game_screen)
		self.name = "Connect 4"
		self.instructions = "Click on a column to drop a circle in it. You win if you form a line of four circles of your color."
		self.player_slot_names = ("red", "yellow")
		self.min_players = 2
		self.max_players = 2
		self.keys_to_request = ["move-n", "move-ne", "move-e", "move-se", "move-s", "move-sw", "move-w", "move-nw", "use-item"]
		self.keys_required   = ["move-e", "move-w", "use-item"]

	def init_game(self):
		self.set_screen_size(7, 7, BoardGameTile.tile_w, BoardGameTile.tile_h)
		self.set_screen_params(tileset_url=BoardGameTile.url, clickable=True)
		self.draw_initial_board()

	def start_game(self):
		self.draw_initial_board()
		self.start_turn(random.randint(0, 1))
		self.placed_tile_count = 0
		self.game_ongoing = True

	def draw_initial_board(self):
		self.set_screen_tile_rect(0, 0, 7, 6, BoardGameTile.connect4_tile)
		self.set_screen_tile(0, 6, BoardGameTile.connect4_leg_l)
		self.set_screen_tile(6, 6, BoardGameTile.connect4_leg_r)

	def start_turn(self, player):
		self.current_player = player
		self.set_screen_tile(2, 6, BoardGameTile.current_player)
		self.set_screen_tile(3, 6, BoardGameTile.player_yellow if self.current_player else BoardGameTile.player_red)

		# Try and position it in the middle
		self.use_cursor = self.game_screen.current_players[player].took_keys
		self.key_cursor_x = 2
		self.cursor_next()
		self.draw_cursor()

	# ---------------------------------

	def cursor_prev(self):
		original_value = self.key_cursor_x
		while True:
			self.key_cursor_x -= 1
			if self.key_cursor_x == -1:
				self.key_cursor_x = 6
			if self.key_cursor_x == original_value or self.get_screen_tile(self.key_cursor_x, 0) == BoardGameTile.connect4_tile:
				return

	def cursor_next(self):
		original_value = self.key_cursor_x
		while True:
			self.key_cursor_x += 1
			if self.key_cursor_x == 7:
				self.key_cursor_x = 0
			if self.key_cursor_x == original_value or self.get_screen_tile(self.key_cursor_x, 0) == BoardGameTile.connect4_tile:
				return

	def draw_cursor(self):
		self.set_screen_tile_rect(0, 0, 7, 1, None, True)
		if self.use_cursor:
			self.set_screen_tile(self.key_cursor_x, 0, BoardGameTile.connect4_yellow_cursor if self.current_player else BoardGameTile.connect4_red_cursor, True)

	def place_in_column(self, place_x):
		try_y = 6
		while try_y >= 0:
			if self.get_screen_tile(place_x, try_y) == BoardGameTile.connect4_tile:
				break
			try_y -= 1
		else:
			self.tell_player(player, 'That column is full!')
			return
		# Put in the tile
		self.set_screen_tile(place_x, try_y, BoardGameTile.connect4_yellow if self.current_player else BoardGameTile.connect4_red)
		self.placed_tile_count += 1

		# Look for matches
		match_h = set()
		match_v = set()
		match_d1 = set()
		match_d2 = set()
		for y in range(6):
			for x in range(7):
				this = self.get_screen_tile(x, y)
				if this == BoardGameTile.connect4_tile:
					continue
				if this == self.get_screen_tile(x+1, y)   and this == self.get_screen_tile(x+2, y)   and this == self.get_screen_tile(x+3, y): # Horiz
					match_h.add((x,y))
					match_h.add((x+1,y))
					match_h.add((x+2,y))
					match_h.add((x+3,y))
				if this == self.get_screen_tile(x,   y+1) and this == self.get_screen_tile(x,   y+2) and this == self.get_screen_tile(x,   y+3): # Vert
					match_v.add((x,y))
					match_v.add((x,y+1))
					match_v.add((x,y+2))
					match_v.add((x,y+3))
				if this == self.get_screen_tile(x+1, y-1) and this == self.get_screen_tile(x+2, y-2) and this == self.get_screen_tile(x+3, y-3): # /
					match_d1.add((x,y))
					match_d1.add((x+1,y-1))
					match_d1.add((x+2,y-2))
					match_d1.add((x+3,y-3))
				if this == self.get_screen_tile(x+1, y+1) and this == self.get_screen_tile(x+2, y+2) and this == self.get_screen_tile(x+3, y+3): # \
					match_d2.add((x,y))
					match_d2.add((x+1,y+1))
					match_d2.add((x+2,y+2))
					match_d2.add((x+3,y+3))
		if match_h or match_v or match_d1 or match_d2:
			for positions, tile in (
				(match_h, BoardGameTile.connect4_yellow_h if self.current_player else BoardGameTile.connect4_red_h),
				(match_v, BoardGameTile.connect4_yellow_v if self.current_player else BoardGameTile.connect4_red_h),
				(match_d1, BoardGameTile.connect4_yellow_d1 if self.current_player else BoardGameTile.connect4_red_d1),
				(match_d2, BoardGameTile.connect4_yellow_d2 if self.current_player else BoardGameTile.connect4_red_d2)
			):
				for pos in positions:
					self.set_screen_tile(pos[0], pos[1], tile)
			self.send_chat(f'Won by {self.game_screen.current_players[self.current_player].name} (Playing as {self.player_slot_names[self.current_player]})! Click to start a new game.')
			self.game_ongoing = False
			return

		if self.placed_tile_count == 7*6:
			self.send_chat("Draw! Click to start a new game.")
			self.game_ongoing = False
			return

		# Switch to the other player
		self.start_turn(self.current_player ^ 1)

	# ---------------------------------

	def click(self, player, x, y, map_x, map_y):
		if player == None:
			return
		if not self.game_ongoing:
			self.start_game()
			return

		if player != self.current_player:
			self.tell_player(player, f"It's currently {self.player_slot_names[self.current_player]}\'s turn")
		else:
			self.place_in_column(map_x)

	def key_press(self, player, key):
		if player == None:
			return
		if not self.game_ongoing:
			if key == "use-item":
				self.start_game()
			return
		if player != self.current_player:
			return

		if key == "use-item":
			self.place_in_column(self.key_cursor_x)
		elif key == "move-e":
			self.cursor_next()
		elif key == "move-w":
			self.cursor_prev()
		self.draw_cursor()
