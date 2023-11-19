from games.base import *
from games.tilesets import *
import random

eight_directions = ((1,0), (1,1), (0,1), (-1,1), (-1,0), (-1,-1), (0,-1), (1,-1))
player_colors = (BoardGameTile.reversi_white, BoardGameTile.reversi_black)

class GameReversi(GameBase):
	BOARD_W = 8
	BOARD_H = 8
	STATUS_HEIGHT = 1

	name = "Reversi"
	instructions = "See [url]https://en.wikipedia.org/wiki/Reversi[/url]."
	min_players = 2
	max_players = 2
	player_slot_names = ("white", "black")

	def init_game(self, reset=False):
		if not reset:
			self.set_screen_size(self.BOARD_W, self.BOARD_H+self.STATUS_HEIGHT, BoardGameTile.tile_w, BoardGameTile.tile_h)
			self.set_screen_params(tileset_url=BoardGameTile.url, clickable=True)

		self.set_screen_tile_rect(0, self.STATUS_HEIGHT, self.BOARD_W, self.BOARD_H, BoardGameTile.reversi_tile)
		x = self.BOARD_W // 2 - 1
		y = self.BOARD_H // 2 - 1
		self.set_screen_tile(x,   y+self.STATUS_HEIGHT,   BoardGameTile.reversi_black)
		self.set_screen_tile(x+1, y+self.STATUS_HEIGHT,   BoardGameTile.reversi_white)
		self.set_screen_tile(x,   y+1+self.STATUS_HEIGHT, BoardGameTile.reversi_white)
		self.set_screen_tile(x+1, y+1+self.STATUS_HEIGHT, BoardGameTile.reversi_black)

	def start_game(self):
		self.start_turn(random.randint(0, 1))
		self.game_ongoing = True

	def stop_game(self):
		self.game_ongoing = False

	def start_turn(self, player):
		self.current_player = player
		self.set_screen_tile(self.BOARD_W//2-1, 0, BoardGameTile.current_player)
		self.set_screen_tile(self.BOARD_W//2, 0, BoardGameTile.player_black if self.current_player else BoardGameTile.player_white)

	# ---------------------------------

	def find_tile_flips(self, player, try_x, try_y):
		final_color = player_colors[player]

		flips = set()
		for dx, dy in eight_directions:
			current_flips = set()
			x = try_x
			y = try_y
			while True:
				x += dx
				y += dy
				at_xy = self.get_screen_tile(x, y)
				if at_xy == final_color:
					break
				elif at_xy not in player_colors:
					current_flips.clear()
					break
				current_flips.add((x,y))
			flips.update(current_flips)
		return flips

	def player_has_any_matches(self, player):
		for x in range(self.BOARD_W):
			for y in range(self.BOARD_H):
				if self.get_screen_tile(x, y+self.STATUS_HEIGHT) != BoardGameTile.reversi_tile:
					continue
				if self.find_tile_flips(player, x, y+self.STATUS_HEIGHT):
					return True
		return False

	# ---------------------------------

	def click(self, player, x, y, map_x, map_y):
		if player == None:
			return
		if not self.game_ongoing:
			self.init_game(reset=True)
			self.start_game()
			return

		if x % 5 == 0 or y % 5 == 0: # Can't click on the boundaries
			return
		if player != self.current_player:
			self.tell_player(player, f"It's currently {self.player_slot_names[self.current_player]}\'s turn")
			return
		if self.get_screen_tile(map_x, map_y) != BoardGameTile.reversi_tile:
			return
		flips = self.find_tile_flips(player, map_x, map_y)
		if not flips:
			return

		# Flip!
		your_color = player_colors[player]
		for x, y in flips:
			self.set_screen_tile(x, y, your_color)
		self.set_screen_tile(map_x, map_y, your_color)

		# See if the other player even has any moves left
		if self.player_has_any_matches(player ^ 1):
			self.start_turn(player ^ 1)
		elif self.player_has_any_matches(player):
			self.send_chat(f'Skipping {self.player_slot_names[player ^ 1]} because they have no possible moves.')
			self.start_turn(player)
		else:
			total_white = 0
			total_black = 0
			for x in range(self.BOARD_W):
				for y in range(self.BOARD_H):
					at_xy = self.get_screen_tile(x, y+self.STATUS_HEIGHT)
					if at_xy == BoardGameTile.reversi_white:
						total_white += 1
					elif at_xy == BoardGameTile.reversi_black:
						total_black += 1
			self.send_chat(f'Game over! Scores: [table][tr][td]{self.game_screen.current_players[0].name}[/td][td]white[/td][td]{total_white}[/td][/tr][tr][td]{self.game_screen.current_players[1].name}[/td][td]black[/td][td]{total_black}[/td][/tr][/table] Click to start a new game.')
			self.game_ongoing = False

class GameReversiBig(GameReversi):
	BOARD_W = 12
	BOARD_H = 10
