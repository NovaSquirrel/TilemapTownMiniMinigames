from enum import Enum

class TilesetUrl:
	Bitmap4x2      = "https://i.imgur.com/eD7Cypz.png"
	Bitmap4x2_Alt  = "https://i.imgur.com/nBMN56u.png"

class BoardGameTile:
	url = "https://i.imgur.com/kWY8in8.png"
	tile_w = 5
	tile_h = 5

	connect4_tile = (1,0)
	connect4_red       = (0,1)
	connect4_yellow    = (1,1)
	connect4_red_h     = (0,2)
	connect4_yellow_h  = (1,2)
	connect4_red_v     = (0,3)
	connect4_yellow_v  = (1,3)
	connect4_red_d1    = (0,4)
	connect4_yellow_d1 = (1,4)
	connect4_red_d2    = (0,5)
	connect4_yellow_d2 = (1,5)
	connect4_red_cursor    = (0,6)
	connect4_yellow_cursor = (1,6)
	connect4_leg_l     = (0,7)
	connect4_leg_r     = (1,7)

	current_player     = (2,0)
	player_red         = (4,0)
	player_yellow      = (5,0)
	player_white       = (6,0)
	player_black       = (7,0)

	reversi_tile       = (2,1)
	reversi_white      = (2,2)
	reversi_black      = (2,3)
	reversi_white_cursor = (2,4)
	reversi_black_cursor = (2,5)
	reversi_white_x    = (2,6)
	reversi_black_x    = (2,7)

	snake_floor        = (3,0)
	snake_player_u     = (3,1)
	snake_player_r     = (3,2)
	snake_player_d     = (3,3)
	snake_player_l     = (3,4)
	snake_part         = (3,5)
	snake_apple        = (3,6)
	wall               = (3,7)
	
	checker_light_tile = (4,6)
	checker_dark_tile  = (4,7)
	checker_black      = (5,6)
	checker_red        = (5,7)
	checker_black_king = (6,6)
	checker_red_king   = (6,7)
	checker_black_cursor = (7,6)
	checker_red_cursor   = (7,7)
	checker_light_cursor = (7,4)
	checker_dark_cursor  = (7,5)

	# Also there's some bomber tiles

class ColorBombTile: #4x4
	url = "https://i.imgur.com/n3qMpNd.png"
	tile_w = 4
	tile_h = 4
	
	black = (1,0)
	white = (2,0)
	cursor = (3,0)
	gradient_gray = (4,0)
	gradient_blue = (5,0)
	block = (6,0)
	ace = (7,0)

	floor = (0,4)
	wall = (1,4)
	breakable = (2,4)
	fire = (3,4)
	powerup_fire = (4,4)
	powerup_bomb = (5,4)
	powerup_kick = (6,4)
	powerup_shield = (7,4)
	def bomb(player, frame):
		return (player*2+int(frame), 5)
	def player(player):
		return (player, 6)
	exit = (5,6)

	snake_part = (6,6)
	snake_apple = (7,6)

	def digit_top(num):
		return (num & 7, 7 + (2 if num > 7 else 0))
	def digit_bottom(num):
		return (num & 7, 8 + (2 if num > 7 else 0))

	digit_blank_top = (3,9)
	digit_blank_bottom = (3,10)

class BingoTile: #8x8
	url = "https://i.imgur.com/rkA5Y01.png"
	tile_w = 8
	tile_h = 8

	def number_tile(num, red=False):
		return (num & 7, (num >> 3) + (4 if red else 0))
	empty          = (0,0)
	wall           = (0,8)
	player1        = (1,8)
	player2        = (2,8)
	player1_tile   = (3,8)
	player2_tile   = (4,8)
	empty_tile     = (5,8)
	money_tile     = (6,8)
	red_money_tile = (7,8)
	bingo_b_tile   = (0,9)
	bingo_i_tile   = (1,9)
	bingo_n_tile   = (2,9)
	bingo_g_tile   = (3,9)
	bingo_o_tile   = (4,9)
	bingo_tile     = (5,9)

class MiniTownTile: #8x8
	url = "https://i.imgur.com/qWKkK9A.png"
	tile_w = 8
	tile_h = 8

	grass     = (0,1)
	dirt      = (1,1)
	lightwood = (2,1)
	darkwood  = (3,1)
	brownsand  = (4,1)
	purplesand = (5,1)
	redbrick   = (6,1)
	graybrick  = (7,1)
	wallpaper  = (8,1)
	no_texture = (9,1)
	blue_carpet = (10,1)
	ice = (11,1)
	flower = (12,1)
	dot_carpet = (13,1)
	dot_carpet2 = (14,1)
	dot_carpet3 = (15,1)
	gray_tile = (0,2)
	brown_tile = (1,2)
	grass_star = (2,2)
	grass_gem = (3,2)
	grass_coin = (4,2)
	grass_pizza = (5,2)
	grass_eggplant = (6,2)
	grass_coin2 = (7,2)
	grass_heart = (8,2)

	water = (0,3)
	wood_wall = (1,3)
	brick_wall = (2,3)
	stone_wall = (3,3)
	window = (4,3)
	x_block = (5,3)
	cliff = (6,3)
	sign = (7,3)
	bush = (8,3)
	bush2 = (9,3)
	fence = (10,3)
	tree = (11,3)
	bush3 = (12,3)
	rock = (13,3)
	chest = (14,3)
	books = (15,3)
	blue_wall = (0,4)
	red_wall = (1,4)
	green_wall = (2,4)
	orange_wall = (3,4)
	boulder = (4,4)
	checker_wall = (5,4)
	blue_checker_wall = (6,4)
	shiny_wall = (7,4)
	breakable_wall = (8,4)

	color_wall1 = (0,5)
	color_wall2 = (1,5)
	color_wall3 = (2,5)
	color_wall4 = (3,5)
	color_wall5 = (4,5)
	color_wall6 = (5,5)
	color_wall7 = (6,5)
	color_wall8 = (7,5)
	color_wall9 = (8,5)
	color_wall10 = (9,5)
	color_wall11 = (10,5)
	color_wall12 = (11,5)
	color_wall13 = (12,5)
	color_wall14 = (13,5)
	color_wall15 = (14,5)
	color_floor1 = (0,6)
	color_floor2 = (1,6)
	color_floor3 = (2,6)
	color_floor4 = (3,6)
	color_floor5 = (4,6)
	color_floor6 = (5,6)
	color_floor7 = (6,6)
	color_floor8 = (7,6)
	color_floor9 = (8,6)
	color_floor10 = (9,6)
	color_floor11 = (10,6)
	color_floor12 = (11,6)
	color_floor13 = (12,6)
	color_floor14 = (13,6)
	color_floor15 = (14,6)

	enemy1 = (0,7)
	enemy2 = (1,7)

	empty = (0,0)
	player1 = (5,0)
	player2 = (3,0)
	player3 = (1,0)
	player4 = (4,0)
	player5 = (2,0)
	enemy_bullet = (6,0)
	player_bullet = (7,0)
	enemy_bullet2 = (8,0)
	player_bullet2 = (9,0)

	ace = (10,0)
	dither = (11,0)
	button_check = (12,0)
	button_x = (13,0)
	button_prev = (14,0)
	button_next = (15,0)

