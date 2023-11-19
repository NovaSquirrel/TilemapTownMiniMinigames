from games.base import *
from games.tilesets import *
import random

class GameBubblePop(GameBase):
	BOARD_W = 7
	BOARD_H = 12
	SCORE_HEIGHT = 2
	TILE_ROW = 1
	COLORS = 7
	RANDOM_ABOVE = True
	SHIFT_EMPTY_COLUMNS = False
	RANDOM_SIDE = False

	name = "Bubble Pop"
	instructions = "Click on groups of multiple tiles of the same color, in order to clear them!"

	def init_game(self):
		self.set_screen_size(self.BOARD_W, self.BOARD_H+2, ColorBombTile.tile_w, ColorBombTile.tile_h)
		self.set_screen_params(tileset_url=ColorBombTile.url, clickable=True)
		self.start_game()
		self.tick_delay = 0

	def start_game(self):
		while True:
			for y in range(self.BOARD_H):
				for x in range(self.BOARD_W):
					self.set_screen_tile(x, y+self.SCORE_HEIGHT, (random.randint(0, self.COLORS-1), self.TILE_ROW))
			if not self.out_of_moves():
				break
		self.score = 0
		self.best_size = 0
		self.game_ongoing = True
		self.search_on_tick = False
		self.update_score()

	def stop_game(self):
		self.game_ongoing = False

	def update_score(self):
		score_length = 6 - (self.BOARD_W % 1)
		text = ("%%.%dd" % score_length) % self.score
		x = self.BOARD_W // 2 - score_length // 2
		for i in range(score_length):
			o = int(text[i])
			self.set_screen_tile(x+i, 0, ColorBombTile.digit_top(o))
			self.set_screen_tile(x+i, 1, ColorBombTile.digit_bottom(o))

	# ---------------------------------

	def flood_fill(self, x, y):
		found = set()
		color = self.get_screen_tile(x, y)
		if color[1] != self.TILE_ROW:
			return found
		def search(x, y):
			found.add((x,y))
			if self.get_screen_tile(x-1, y) == color and ((x-1, y) not in found):
				search(x-1, y)
			if self.get_screen_tile(x+1, y) == color and ((x+1, y) not in found):
				search(x+1, y)
			if self.get_screen_tile(x, y-1) == color and ((x, y-1) not in found):
				search(x, y-1)
			if self.get_screen_tile(x, y+1) == color and ((x, y+1) not in found):
				search(x, y+1)
		search(x, y)
		return found

	def tick(self):
		if self.tick_delay:
			self.tick_delay -= 1
			return
		if self.search_on_tick:
			keep_going = False
			for y in range(self.SCORE_HEIGHT+self.BOARD_H-1, self.SCORE_HEIGHT-1, -1):
				for x in range(self.BOARD_W):
					color = self.get_screen_tile(x, y)
					if color[1] == 3:
						self.set_screen_tile(x, y, ColorBombTile.black)
						if self.RANDOM_ABOVE:
							keep_going = True
						#self.set_screen_tile(x, y, ColorBombTile.black if (y != self.SCORE_HEIGHT or not self.RANDOM_ABOVE) else (random.randint(0, self.COLORS-1), self.TILE_ROW))
					elif color == ColorBombTile.black:
						for drop_y in range(y, 2, -1):
							above = self.get_screen_tile(x, drop_y-1)
							self.set_screen_tile(x, drop_y, above)
						# Random color at the top
						self.set_screen_tile(x, 2, (random.randint(0, self.COLORS-1), self.TILE_ROW) if self.RANDOM_ABOVE else ColorBombTile.black)

			# Move empty columns over, for SameGame
			if self.SHIFT_EMPTY_COLUMNS:
				for x in range(self.BOARD_W):
					if all(self.get_screen_tile(x, y) == ColorBombTile.black for y in range(self.SCORE_HEIGHT, self.SCORE_HEIGHT+self.BOARD_H)):
						for x2 in range(x, self.BOARD_W-1):
							for y in range(self.SCORE_HEIGHT, self.SCORE_HEIGHT+self.BOARD_H):
								self.set_screen_tile(x2, y, self.get_screen_tile(x2+1, y))
						for y in range(self.SCORE_HEIGHT, self.SCORE_HEIGHT+self.BOARD_H):
							self.set_screen_tile(self.BOARD_W-1, y, (random.randint(0, self.COLORS-1), self.TILE_ROW) if self.RANDOM_SIDE else ColorBombTile.black)

			# Need to keep going?
			if not keep_going:
				for x in range(self.BOARD_W):
					bottom_black = None
					top_non_black = None
					for y in range(self.SCORE_HEIGHT, self.SCORE_HEIGHT+self.BOARD_H):
						color = self.get_screen_tile(x, y)
						if color[1] == 3:
							keep_going = True
							break
						if color == ColorBombTile.black:
							bottom_black = y
						elif top_non_black == None:
							top_non_black = y
					if bottom_black and top_non_black and bottom_black > top_non_black:
						keep_going = True
					if keep_going:
						break

			if not keep_going:
				self.search_on_tick = False
				if self.out_of_moves():
					self.game_ongoing = False
					self.send_chat(f'You\'re out of moves! Final score: [b]{self.score}[/b]. Biggest pop: {self.best_size}. Click score to start a new game. ')

	def out_of_moves(self):
		for y in range(self.SCORE_HEIGHT, self.SCORE_HEIGHT+self.BOARD_H):
			for x in range(self.BOARD_W):
				if len(self.flood_fill(x, y)) > 1:
					return False
		return True

	def click(self, player, x, y, map_x, map_y):
		if player == None:
			return
		if not self.game_ongoing:
			if map_y < self.SCORE_HEIGHT:
				self.start_game()
				return
		if map_y < self.SCORE_HEIGHT:
			return

		# Make sure you're clicking on the right tile type
		color = self.get_screen_tile(map_x, map_y)
		if color[1] != self.TILE_ROW:
			return

		# How big is the group?
		fill = self.flood_fill(map_x, map_y)
		count = len(fill)
		if count > 1:
			self.score += (count-1) ** 2
			self.update_score()
		else:
			return
		self.best_size = max(self.best_size, count)

		for pos in fill:
			self.set_screen_tile(pos[0], pos[1], (color[0], 3)) # Popping frame
		self.tick_delay = 1
		self.search_on_tick = True

class GameBubblePopSquare(GameBubblePop):
	BOARD_W = 10
	BOARD_H = 10
	name = "Bubble Pop (square)"

class GameBubblePopMax(GameBubblePop):
	BOARD_W = 16
	BOARD_H = 14
	name = "Bubble Pop (BIG)"

class GameBubblePopMultiplayer(GameBubblePop):
	BOARD_W = 16
	BOARD_H = 14
	name = "Bubble Pop (multiplayer)"

	def __init__(self, game_screen):
		super().__init__(game_screen)
		self.max_players = 99

class GameBubblePopSameGame(GameBubblePop):
	BOARD_W = 12
	BOARD_H = 12
	COLORS = 5
	RANDOM_ABOVE = False
	SHIFT_EMPTY_COLUMNS = True
	name = "SameGame"

class GameBubblePopSameGameExtended(GameBubblePop):
	BOARD_W = 12
	BOARD_H = 12
	COLORS = 5
	RANDOM_ABOVE = False
	SHIFT_EMPTY_COLUMNS = True
	RANDOM_SIDE = True
	name = "SameGame (extended)"
