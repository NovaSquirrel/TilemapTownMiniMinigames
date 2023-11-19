import json, time
from game_shared import *
from games.directory import game_directory

entity_request_count = 1

class GamePlayer(object):
	def __init__(self, entity_id, username, name):
		self.took_keys = False      # take_controls was used
		self.keys_available = set() # Which keys the user's client has, out of the ones that were requested
		self.last_input_at = None   # Last time.time() the player sent in an input

		self.entity_id = entity_id
		self.username = username
		self.name = name

class GameScreen(object):
	def __init__(self, town):
		self.entity_id = None
		self.entity_requested = False   # If true, there was already an attempt at making the entity
		self.town = town

		self.game = None                # The currently active game!!
		self.encoded_game_screen = None # For detecting when the screen actually needs to be re-sent

		# Management
		self.current_players = []       # Players who are currently in the game, or who will be when it starts; in order
		self.current_players_by_id = {} # Same, but as a dictionary
		self.waiting_for_keys = {}      # Users who will join as soon as their controls are taken

		self.game_in_progress = False   # Game is currently going on and no one new can join
		self.last_input_at = None       # Last input the game got from anyone, to know when to stop the game due to inactivity

	# --- Setup

	def setup_preexisting(self, e_id):
		# Use an entity that already exists
		self.entity_requested = True
		self.entity_id = e_id
		self.town.game_screens_by_entity_id[e_id] = self
		self.town.send_cmd_command(f'message_forwarding set {self.entity_id} MSG,EXT,ERR,PRI')

		self.change_game(game_directory['reversi']) # Temporary

	def setup_by_create(self):
		# Create a new entity and then use it
		global entity_request_count

		def created(id):
			self.town.send_command("BAG", {'update': {"id": id, "name": "A cool game!", "pic": [-1, 3, 5]}}) # Use invisible wall tile
			self.setup_preexisting(id)
			self.town.send_command("MOV", {'rc': id, 'new_map': 61, 'to': [3,3]}) # Temporary

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

	def start_game(self):
		if not self.game:
			return
		self.waiting_for_keys.clear()
		self.game_in_progress = True
		self.send_chat(f'Starting [b]{self.game.name}[/b]! Players: {self.player_name_list()}. [bot-message-button=Stop game]stop[/bot-message-button]')
		self.game.start_game()
		self.last_input_at = time.time() # Start counting from now

	def stop_game(self, inactivity=False):
		if not self.game:
			return
		for player in self.current_players:
			self.release_keys(player)
		self.current_players = []
		self.current_players_by_id.clear()
		self.waiting_for_keys.clear()

		if self.game_in_progress:
			self.game_in_progress = False
			self.game.stop_game()
			self.send_chat(f'Stopping [b]{self.game.name}[/b]{" due to inactivity" if inactivity else ""}')
		else:
			self.send_chat(f'Canceling [b]{self.game.name}[/b]')

	def change_game(self, game):
		if self.game_in_progress:
			self.stop_game()
		self.game = game(self)
		self.game.init_game()
		self.refresh_screen_if_needed()

	def player_num_from_id(self, id):
		by_id = self.current_players_by_id.get(id, None)
		if by_id == None:
			return None
		by_id.last_input_at = time.time()
		for i, player in enumerate(self.current_players):
			if player is by_id:
				return i
		return None

	def player_name_list(self):
		if self.game and self.game.player_slot_names:
			return ", ".join(f'{self.current_players[i].name} ({self.game.player_slot_names[i]})' for i in range(len(self.current_players)))
		else:
			return ", ".join(_.name for _ in self.current_players)

	def request_keys(self, player):
		self.town.send_command("EXT", {"take_controls": {"id": player.entity_id, "keys": self.game.keys_to_request, "pass_on": self.game.keys_pass_on, "key_up": self.game.receive_key_up}, "rc": self.entity_id})

	def release_keys(self, player):
		if player.took_keys:
			self.town.send_command("EXT", {"take_controls": {"id": player.entity_id, "keys": []}, "rc": self.entity_id})
			player.took_keys = False

	def join_game(self, player):
		user_id = player.entity_id
		self.waiting_for_keys.pop(user_id, None)
		if self.game_in_progress:
			self.tell_user(user_id, "Sorry, the game is already in progress!")
			return False
		elif user_id in self.current_players_by_id:
			self.tell_user(user_id, "You already joined! [bot-message-button=Leave]leave[/bot-message-button]")
			return False
		elif len(self.current_players) >= self.game.max_players:
			self.tell_user(user_id, "Sorry, there are already too many players!")
			return False
		else:
			self.current_players.append(player)
			self.current_players_by_id[user_id] = player

			if self.game.max_players == 1:
				self.tell_user(user_id, f'You start [b]{self.game.name}[/b]! [bot-message-button=Leave]leave[/bot-message-button]')
				self.start_game()

			if len(self.current_players) >= self.game.max_players:
				self.tell_user(user_id, f'You join [b]{self.game.name}[/b]{", and now the game is full" if self.game.max_players > 1 else ""}! [bot-message-button=Leave]leave[/bot-message-button]')
				self.start_game()
			else:
				self.tell_user(user_id, f'You join [b]{self.game.name}[/b]! [bot-message-button=Leave]leave[/bot-message-button]')

				self.send_chat(f'{player.name} joins [b]{self.game.name}[/b]! Players: {len(self.current_players)}/{self.game.min_players}{" [bot-message-button=Start game]start[/bot_message-button]" if len(self.current_players) >= self.game.min_players else ""}')
		return True

	def receive_private_message(self, user_id, username, name, text):
		if text == "gamelist":
			self.tell_user(user_id, "Games: " + ", ".join(f"[bot-message-button={x}]game {x}[/bot-message-button]" for x in game_directory.keys()))
		elif text.startswith("game "):
			gamename = text[5:].strip()
			if gamename in game_directory:
				self.change_game(game_directory[gamename])
				print("New game "+gamename)
			else:
				print("Can't find "+gamename)
		elif text == "help":
			self.tell_user(user_id, "Commands: [bot-message-button]join[/bot-message-button], [bot-message-button]joinclick[/bot-message-button], [bot-message-button]joinkeys[/bot-message-button], [bot-message-button]leave[/bot-message-button], [bot-message-button]instructions[/bot-message-button], [bot-message-button]start[/bot-message-button], [bot-message-button]stop[/bot-message-button], [bot-message-button]gamelist[/bot-message-button], [bot-message-button]game[/bot-message-button]")

		if not self.game:
			return

		if text == "join":
			if not self.game_in_progress:
				player = GamePlayer(user_id, username, name)
				if self.game.keys_to_request:
					self.waiting_for_keys[user_id] = player
					self.request_keys(player)
				else:
					self.join_game(player)
			else:
				self.tell_user(user_id, "Sorry, the game is already in progress!")
		elif text == "joinclick" and not self.game.key_mode_only:
			if not self.game_in_progress:
				self.join_game(GamePlayer(user_id, username, name))
			else:
				self.tell_user(user_id, "Sorry, the game is already in progress!")
		elif text == "joinkeys" and len(self.game.keys_to_request):
			if not self.game_in_progress:
				player = GamePlayer(user_id, username, name)
				self.waiting_for_keys[user_id] = player
				self.request_keys(player)
			else:
				self.tell_user(user_id, "Sorry, the game is already in progress!")

		elif text == "leave":
			if user_id not in self.current_players_by_id:
				return
			if self.game_in_progress:
				self.stop_game()
			else:
				player =  self.current_players_by_id[user_id]
				self.release_keys(player)
				del self.current_players_by_id[user_id]
				self.current_players.remove(player)
				self.tell_user(user_id, f'You leave [b]{self.game.name}[/b]')
		elif text == "instructions":
			self.tell_user(user_id, f'How to play [b]{self.game.name}[/b]: {self.game.instructions}')
		elif text == "start":
			if not self.game_in_progress:
				if user_id not in self.current_players_by_id:
					self.tell_user(user_id, "You aren't one of the players!")
				elif self.game and len(self.current_players) >= self.game.min_players:
					self.start_game()
				else:
					self.tell_user(user_id, "There aren't enough players yet!")
			else:
				self.tell_user(user_id, "Game was already started")
		elif text == "stop":
			if self.game_in_progress:
				if user_id not in self.current_players_by_id:
					self.tell_user(user_id, "You aren't one of the players!")
					return
				self.stop_game()
			else:
				self.tell_user(user_id, "No game in progress")

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
					self.last_input_at = time.time()
					arg2     = arg["entity_click"]
					a_id     = arg2.get("id", None)
					pixel_x  = arg2.get("x", 0)
					pixel_y  = arg2.get("y", 0)
					a_button = arg2.get("button", 0)
					a_target = arg2.get("target", "entity")
					player = self.player_num_from_id(a_id)
					if player != None and self.game_in_progress:
						map_x = pixel_x//self.game.tile_w
						map_y = pixel_y//self.game.tile_h
						if map_x >= 0 and map_y >= 0 and map_x < self.game.map_w  and map_y < self.game.map_h:
							self.game.click(player, pixel_x, pixel_y, map_x, map_y)
							self.refresh_screen_if_needed()
					elif player != None:
						self.tell_user(a_id, "You already joined! [bot-message-button=Leave]leave[/bot-message-button]")
					else:
						if self.game_in_progress or len(self.current_players) >= self.game.max_players:
							self.tell_user(a_id, f'{self.game.name} is already in use by {self.player_name_list()}. You can still look at the instructions: [bot-message-button=Instructions]instructions[/bot-message-button]')
						else:
							self.tell_user(a_id, f'{"Join" if self.game.max_players > 1 else "Start"} [b]{self.game.name}[/b]? [bot-message-button=Instructions]instructions[/bot-message-button] {"[bot-message-button=🖱️Join]joinclick[/bot-message-button] [bot-message-button=🎮Join]joinkeys[/bot-message-button]" if (not self.game.key_mode_only and len(self.game.keys_to_request)) else "[bot-message-button=Join game]join[/bot-message-button]"}')

			elif "key_press" in arg:
				if self.game and self.game_in_progress:
					self.last_input_at = time.time()
					arg2 = arg["key_press"]
					a_id = arg2.get("id", None)
					a_key = arg2.get("key", None)
					a_down = arg2.get("down", True)
					player = self.player_num_from_id(a_id)

					if a_down:
						self.game.key_press(player, a_key)
					else:
						self.game.key_release(player, a_key)
					self.refresh_screen_if_needed()

			elif "took_controls" in arg:
				if not self.game:
					return
				arg2 = arg["took_controls"]
				a_id     = arg2.get("id", None)
				a_keys   = arg2.get("keys", None)
				a_accept = arg2.get("accept", True)
				if a_id in self.waiting_for_keys and a_accept:
					player = self.waiting_for_keys[a_id]
					player.took_keys = True
					player.keys_available = set(a_keys)
					if all(key in player.keys_available for key in self.game.keys_required):
						self.join_game(player)
					elif player.keys_available: # Make sure it's not an empty set
						self.release_keys(player)
						self.tell_user(a_id, "Your client doesn't support some keys this game needs")
			elif "bot_message_button" in arg:
				self.last_input_at = time.time()
				if self.game:
					arg2 = arg["bot_message_button"]
					self.receive_private_message(arg2.get("id", None), arg2.get("username"), arg2.get("name"), arg2.get("text", None))

		elif message_type == "ERR":
			ext_type = arg.get("ext_type", None)
			if ext_type == "take_controls":
				code = arg.get("code", None)
				detail = arg.get("detail", None)
				subject_id = arg.get("subject_id", None)
				if code == "missing_permission" and detail == "minigame" and subject_id in self.waiting_for_keys:
					self.send_cmd_command(f'requestpermission {subject_id} minigame')

		elif message_type == "PRI":
			if arg.get("receive", False):
				self.receive_private_message(arg.get("id", None), arg.get("username"), arg.get("name"), arg.get("text", None))

		elif message_type == "MSG":
			if "data" in arg and "request_accepted" in arg["data"]:
				accepted = arg["data"]["request_accepted"]
				request_id = accepted.get("id", None)
				request_type = accepted.get("type", None)
				request_data = accepted.get("data", None)
				if request_type == "tempgrant" and request_data == "minigame" and request_id in self.waiting_for_keys:
					self.request_keys(self.waiting_for_keys[request_id])
			if "buttons" in arg:
				for command in arg["buttons"][1::2]:
					if command.startswith('tpaccept '):
						self.send_cmd_command(command)

	def tick(self):
		if not self.game:
			return
		if self.game_in_progress:
			if time.time() > (self.last_input_at + self.game.timeout):
				self.stop_game(inactivity=True)
			else:
				self.game.tick()
				self.refresh_screen_if_needed()
		elif len(self.current_players) and time.time() > (self.last_input_at + 180):
			self.stop_game()

	def refresh_screen_if_needed(self):
		if not self.game or not (self.game.game_map_changed or self.game.game_map_config_changed):
			return
		out = {}

		if self.game.game_map_config_changed:
			self.game.game_map_config_changed = False
			out['mini_tilemap'] = {"visible": self.game.visible, "clickable": self.game.clickable, "map_size": [self.game.map_w, self.game.map_h], "tile_size": [self.game.tile_w, self.game.tile_h], "tileset_url": self.game.tileset_url, "offset": self.game.offset, "transparent_tile": self.game.transparent_tile}

		if self.game.game_map_changed:
			self.game.game_map_changed = False
			encoded = self.game.encode_screen()
			if encoded != self.encoded_game_screen: # Did the map actually change?
				out['mini_tilemap_data'] = {"data": encoded}
				self.encoded_game_screen = encoded

		if out:
			self.town.send_command("WHO", {"update": out, "rc": self.entity_id})
