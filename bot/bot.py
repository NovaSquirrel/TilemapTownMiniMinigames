#!/usr/bin/env python
import asyncio
from game_shared import *
from tilemap_town import TilemapTown
from game_entity import GameScreen

async def main():
	async with asyncio.TaskGroup() as tg:
		#town = TilemapTown('wss://novasquirrel.com/townws/')
		town = TilemapTown('ws://localhost:12550')
		tg.create_task(town.run_timer())
		tg.create_task(town.run_client())

asyncio.run(main())
