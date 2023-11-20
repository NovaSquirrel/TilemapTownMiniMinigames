from games.base import *
from games.tilesets import *
import random

class GameBingo(GameBase):
	BOARD_W = 5
	BOARD_H = 5
	WALLS = 0
	WIN_BY_COUNT = False

	name = "Bingo"
	instructions = "See https://en.wikipedia.org/wiki/Panel_Action_Bingo"
	player_slot_names = ("blue", "yellow")
	min_players = 2
	max_players = 2
	keys_to_request = ["move-n", "move-ne", "move-e", "move-se", "move-s", "move-sw", "move-w", "move-nw", "use-item"]
	keys_required   = ["move-n", "move-e", "move-s", "move-w"]
	key_mode_only   = True

	def init_game(self):
		self.set_screen_size(self.BOARD_W, self.BOARD_H, BingoTile.tile_w, BingoTile.tile_h)
		self.set_screen_params(tileset_url=BingoTile.url, clickable=True)
		self.game_ongoing = False
		self.randomize_board()

	def start_game(self):
		self.game_ongoing = True
		self.randomize_board()
		self.highlight_next_to_get()

	def stop_game(self):
		self.game_ongoing = False

	def pick_random_player_pos(self, avoid=None):
		if avoid != None:
			avoid = avoid[1] * self.BOARD_H + avoid[0] # Convert it to an index
		while True:
			i = random.randint(0, self.BOARD_W * self.BOARD_H - 1)
			if i != avoid and self.board[i] != None:
				return (i % self.BOARD_W, i // self.BOARD_H)

	def is_solid_at(self, x, y, avoid=None):
		if (x,y) == avoid:
			return True
		t = self.get_board_at(x, y)
		return t == None		

	def get_board_at(self, x, y):
		if x < 0 or x >= self.BOARD_W or y < 0 or y >= self.BOARD_H:
			return None
		return self.board[y * self.BOARD_W + x]

	def randomize_board(self):
		self.stop_at_number = self.BOARD_W * self.BOARD_H - self.WALLS
		self.board = [x for x in range(self.stop_at_number)] + ([None] * self.WALLS)
		random.shuffle(self.board)
		for y in range(self.BOARD_H):
			for x in range(self.BOARD_W):
				t = self.board[y * self.BOARD_W + x]
				if t == None:
					self.set_screen_tile(x, y, BingoTile.wall)
				else:
					self.set_screen_tile(x, y, BingoTile.number_tile(t+1))
		self.set_screen_tile_rect(0, 0, self.BOARD_W, self.BOARD_H, None, True) # Clear the Over layer
		self.next_number_to_get = 0

		if self.game_ongoing:
			p1_pos = self.pick_random_player_pos()
			p2_pos = self.pick_random_player_pos(p1_pos)
			self.player_pos = [p1_pos, p2_pos]
			self.draw_players()

	def draw_players(self):
		self.set_screen_tile_rect(0, 0, self.BOARD_W, self.BOARD_H, None, True) # Clear the Over layer
		self.set_screen_tile(self.player_pos[0][0], self.player_pos[0][1], BingoTile.player1, True)
		self.set_screen_tile(self.player_pos[1][0], self.player_pos[1][1], BingoTile.player2, True)

	def highlight_next_to_get(self):
		i = self.board.index(self.next_number_to_get)
		x = i % self.BOARD_W
		y = i // self.BOARD_W
		self.set_screen_tile(x, y, BingoTile.number_tile(self.next_number_to_get+1, red=True))

	def check_for_touching_next_number(self, who):
		def check_player(player):
			pos = self.player_pos[player]
			under_player = self.get_board_at(pos[0], pos[1])
			if under_player != self.next_number_to_get:
				return False
			self.set_screen_tile(pos[0], pos[1], BingoTile.player2_tile if player else BingoTile.player1_tile)

			if not self.WIN_BY_COUNT:
				# Check for bingo
				matches = set()
				# Horizontal
				for y in range(self.BOARD_H):
					this = self.get_screen_tile(0, y)
					if this not in (BingoTile.player1_tile, BingoTile.player2_tile):
						continue
					if this == self.get_screen_tile(1, y) and this == self.get_screen_tile(2, y) and this == self.get_screen_tile(3, y) and this == self.get_screen_tile(4, y):
						matches.add((0,y,0))
						matches.add((1,y,1))
						matches.add((2,y,2))
						matches.add((3,y,3))
						matches.add((4,y,4))

				# Vertical
				for x in range(self.BOARD_W):
					this = self.get_screen_tile(x, 0)
					if this not in (BingoTile.player1_tile, BingoTile.player2_tile):
						continue
					if this == self.get_screen_tile(x, 1) and this == self.get_screen_tile(x, 2) and this == self.get_screen_tile(x, 3) and this == self.get_screen_tile(x, 4):
						matches.add((x,0,0))
						matches.add((x,1,1))
						matches.add((x,2,2))
						matches.add((x,3,3))
						matches.add((x,4,4))

				#Diagonal \
				this = self.get_screen_tile(0, 0)
				if this in (BingoTile.player1_tile, BingoTile.player2_tile):
					if this == self.get_screen_tile(1, 1) and this == self.get_screen_tile(2, 2) and this == self.get_screen_tile(3, 3) and this == self.get_screen_tile(4, 4):
						matches.add((0,0,0))
						matches.add((1,1,1))
						matches.add((2,2,2))
						matches.add((3,3,3))
						matches.add((4,4,4))

				# Diagonal /
				this = self.get_screen_tile(0, 4)
				if this in (BingoTile.player1_tile, BingoTile.player2_tile):
					if this == self.get_screen_tile(1, 3) and this == self.get_screen_tile(2, 2) and this == self.get_screen_tile(3, 1) and this == self.get_screen_tile(4, 0):
						matches.add((0,4,0))
						matches.add((1,3,1))
						matches.add((2,2,2))
						matches.add((3,1,3))
						matches.add((4,0,4))

				if matches:
					for pos in matches:
						tile_tx = pos[2]
						tile_ty = BingoTile.bingo_b_tile_2[1] if player else BingoTile.bingo_b_tile_1[1]
						self.set_screen_tile(pos[0], pos[1], (tile_tx, tile_ty))
					self.set_screen_tile_rect(0, 0, self.BOARD_W, self.BOARD_H, None, True) # Clear the Over layer

					self.send_chat(f'Won by {self.game_screen.current_players[player].name} (playing as {self.player_slot_names[player]})! Click to start a new game.')
					self.game_ongoing = False
					return False

			# Otherwise point out the next target
			self.next_number_to_get += 1
			if self.next_number_to_get >= self.stop_at_number:
				p1_count = 0
				p2_count = 0
				for y in range(self.BOARD_H):
					for x in range(self.BOARD_W):
						t = self.get_screen_tile(x, y)
						if t == BingoTile.player1_tile:
							p1_count += 1
						if t == BingoTile.player2_tile:
							p2_count += 1

				winner = 0 if p1_count > p2_count else 1
				if p1_count != p2_count:
					self.send_chat(f'Won by {self.game_screen.current_players[winner].name} (playing as {self.player_slot_names[winner]})! Click to start a new game.')
				else:
					self.send_chat(f'Draw! Click to start a new game.')
				self.game_ongoing = False
				return False
			self.highlight_next_to_get()
			return True

		if check_player(who):
			check_player(who ^ 1)

	# ---------------------------------

	def click(self, player, x, y, map_x, map_y):
		if player == None:
			return
		if not self.game_ongoing:
			self.start_game()
			return

	def key_press(self, player, key):
		if player == None:
			return
		if not self.game_ongoing:
			if key == "use-item":
				self.start_game()
			return

		try_xy = None
		if key == "move-n":
			try_xy = (0, -1)
		elif key == "move-e":
			try_xy = (1, 0)
		elif key == "move-s":
			try_xy = (0, 1)
		elif key == "move-w":
			try_xy = (-1, 0)
		else:
			return
		other_player = self.player_pos[player ^ 1]
		if self.is_solid_at(self.player_pos[player][0] + try_xy[0], self.player_pos[player][1] + try_xy[1], avoid=other_player):
			return
		self.player_pos[player] = (self.player_pos[player][0] + try_xy[0], self.player_pos[player][1] + try_xy[1])

		# Check for moving onto the current tile
		self.check_for_touching_next_number(player)
		if self.game_ongoing:
			self.draw_players()

class GameBingo1Wall(GameBingo):
	WALLS = 1

class GameBingo2Walls(GameBingo):
	WALLS = 2

class GameBingoMole(GameBingo):
	WIN_BY_COUNT = True
	name = "Not Bingo"

class GameBingoMoleWalls(GameBingo):
	WIN_BY_COUNT = True
	WALLS = 2
	name = "Not Bingo"
