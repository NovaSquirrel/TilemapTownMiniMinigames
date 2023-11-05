import json, time
from game_shared import *
from games.game_directory import game_directory

entity_request_count = 1

class GamePlayer(object):
	def __init__(self, entity_id):
		self.entity_id = entity_id
		self.took_keys = False
		self.keys_available = set()
		self.last_input_at = None

class GameScreen(object):
	def __init__(self, town):
		self.entity_id = None
		self.entity_requested = False # If true, there was already an attempt at making the entity
		self.town = town

		self.game = None
		self.encoded_game_screen = None

		# Management
		self.current_players = []

	# --- Setup

	def setup_preexisting(self, e_id):
		# Use an entity that already exists
		self.entity_requested = True
		self.entity_id = e_id
		self.town.game_screens_by_entity_id[e_id] = self
		self.town.send_cmd_command(f'message_forwarding set {self.entity_id} MSG,EXT,ERR,PRI')

		self.change_game(game_directory['connect_4'])

	def setup_by_create(self):
		# Create a new entity and then use it
		global entity_request_count

		def created(id):
			print("Created "+str(id))
			self.town.send_command("BAG", {'update': {"id": id, "name": "A cool game!"}})
			self.setup_preexisting(id)
			self.town.send_command("MOV", {'rc': id, 'new_map': 61, 'to': [1,1]})

		if self.entity_requested:
			return
		self.entity_requested = True

		request_name = 'temp_entity_' + str(entity_request_count)
		self.town.callbacks_for_creates[request_name] = created
		self.town.send_command("BAG", {'create': {"name": request_name, "temp": True, "type": "generic", "delete_on_logout": True}})
		entity_request_count += 1

	# --- Utilities for games to use

	def send_chat(self, text):
		if self.entity_id == None:
			return
		self.town.send_command("MSG", {"text": text, "rc": self.entity_id})

	def tell_user(self, user, text):
		self.send_cmd_command("tell %s %s" % (user, text))

	def send_cmd_command(self, command):
		if self.entity_id == None:
			return
		self.town.send_command("CMD", {"text": command, "rc": self.entity_id})

	# --- Management

	def change_game(self, game):
		self.game = game(self)
		self.game.init_game()
		self.refresh_screen_if_needed()

	def player_num_from_id(self, id):
		if id in self.current_players:
			return self.current_players.index(id)
		return None

	def request_keys(self, command):
		pass

	def forward_message_to(self, message):
		if len(message)<3:
			return

		message_type = message[0:3]
		arg = {}
		if len(message) > 4:
			arg = json.loads(message[4:])

		# React to the message
		if message_type == "EXT":
			if "entity_click" in arg:
				if self.game:
					arg2     = arg["entity_click"]
					a_id     = arg2.get("id", None)
					pixel_x  = arg2.get("x", 0)
					pixel_y  = arg2.get("y", 0)
					a_button = arg2.get("button", 0)
					a_target = arg2.get("target", "entity")
					player = self.player_num_from_id(a_id)
					
					map_x = pixel_x//self.game.tile_w
					map_y = pixel_y//self.game.tile_h
					if map_x >= 0 and map_y >= 0 and map_x < self.game.map_w  and map_y < self.game.map_h:
						self.game.click(player, pixel_x, pixel_y, map_x, map_y)
						self.refresh_screen_if_needed()
			elif "key_press" in arg:
				if self.game:
					arg2 = arg["key_press"]
					a_id = arg2.get("id", None)
					a_key = arg2.get("key", None)
					a_down = arg2.get("down", True)
					player = self.player_num_from_id(a_id)

					if self.game:
						if a_down:
							self.game.key_press(self, player, key)
						else:
							self.game.key_release(self, player, key)
					self.refresh_screen_if_needed()

			elif "took_controls" in arg:
				pass

		elif message_type == "ERR":
			pass
		elif message_type == "PRI":
			pass
		elif message_type == "MSG":
			if "data" in arg and "request_accepted" in arg["data"]:
				accepted = arg["data"]["request_accepted"]
				request_id = accepted.get("id", None)
				request_type = accepted.get("type", None)
				request_data = accepted.get("data", None)
				if request_type == "tempgrant" and request_data == "minigame":
					print("Minigame granted")
					pass

	def tick(self):
		if not self.game:
			return
		self.game.tick()
		self.refresh_screen_if_needed()

	def refresh_screen_if_needed(self):
		if not self.game or not (self.game.game_map_changed or self.game.game_map_config_changed):
			return
		out = {}

		if self.game.game_map_config_changed:
			self.game.game_map_config_changed = False
			out['mini_tilemap'] = {"visible": self.game.visible, "clickable": self.game.clickable, "map_size": [self.game.map_w, self.game.map_h], "tile_size": [self.game.tile_w, self.game.tile_h], "tileset_url": self.game.tileset_url, "offset": self.game.offset}

		if self.game.game_map_changed:
			self.game.game_map_changed = False
			encoded = self.game.encode_screen()
			if encoded != self.encoded_game_screen: # Did the map actually change?
				out['mini_tilemap_data'] = {"data": encoded}
				self.encoded_game_screen = encoded

		if out:
			self.town.send_command("WHO", {"update": out, "rc": self.entity_id})
