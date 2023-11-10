from games.base import *
from games.tilesets import *
import random

BOARD_W = 7
BOARD_H = 12
SCORE_HEIGHT = 2
TILE_ROW = 1

class GameBubblePop(GameBase):
	def __init__(self, game_screen):
		super().__init__(game_screen)
		self.name = "Bubble Pop"
		self.instructions = "Click on groups of multiple tiles of the same color, in order to clear them!"

	def init_game(self):
		self.set_screen_size(7, 12+2, ColorBombTile.tile_w, ColorBombTile.tile_h)
		self.set_screen_params(tileset_url=ColorBombTile.url, clickable=True)
		self.start_game()
		self.tick_delay = 0

	def start_game(self):
		while True:
			for y in range(BOARD_H):
				for x in range(BOARD_W):
					self.set_screen_tile(x, y+SCORE_HEIGHT, (random.randint(0, 6), TILE_ROW))
			if not self.out_of_moves():
				break
		self.score = 0
		self.best_size = 0
		self.game_ongoing = True
		self.search_on_tick = False
		self.update_score()

	def update_score(self):
		text = "%.5d" % self.score
		for i in range(5):
			o = int(text[i])
			self.set_screen_tile(1+i, 0, ColorBombTile.digit_top(o))
			self.set_screen_tile(1+i, 1, ColorBombTile.digit_bottom(o))

	# ---------------------------------

	def flood_fill(self, x, y):
		found = set()
		color = self.get_screen_tile(x, y)
		if color[1] != TILE_ROW:
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
			changed_anything = False
			for y in range(SCORE_HEIGHT+BOARD_H-1, SCORE_HEIGHT-1, -1):
				for x in range(BOARD_W):
					color = self.get_screen_tile(x, y)
					if color[1] == 3:
						self.set_screen_tile(x, y, ColorBombTile.black)
						changed_anything = True
					elif color == ColorBombTile.black:
						for drop_y in range(y, 2, -1):
							self.set_screen_tile(x, drop_y, self.get_screen_tile(x, drop_y-1))
						# Random color at the top
						self.set_screen_tile(x, 2, (random.randint(0, 6), TILE_ROW))
						changed_anything = True
			if not changed_anything:
				self.search_on_tick = False
				if self.out_of_moves():
					self.game_ongoing = False
					self.send_chat(f'No more moves! Final score: [b]{self.score}[/b]. Biggest pop: {self.best_size}. Click to start a new game.')

	def out_of_moves(self):
		for y in range(SCORE_HEIGHT, SCORE_HEIGHT+BOARD_H):
			for x in range(BOARD_W):
				if len(self.flood_fill(x, y)) > 1:
					return False
		return True

	def click(self, player, x, y, map_x, map_y):
		if player == None or map_y < SCORE_HEIGHT:
			return
		if not self.game_ongoing:
			self.start_game()
			return

		# Make sure you're clicking on the right tile type
		color = self.get_screen_tile(map_x, map_y)
		if color[1] != TILE_ROW:
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
