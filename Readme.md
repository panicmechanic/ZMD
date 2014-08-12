Zeus must die - A python roguelike based on the libtcod tutorial.

Mission statement:

ZMD is a roguelike in which you play an ancient Greek gladiator, hunting a bezerk Zeus.
You seek retribution and will have to journey to the top of Mount Olympus to claim your
prize. On the way you will encounter many different randomised level types; forests,
dungeons, the sea of the dead and the infamous Mt. Olympus. You will have to outwit
great foes, avoid traps, solve puzzles and battle mythic monsters.

The game seeks to (eventually) have a feeling of undertaking a great journey, different
every time you play. As inspired by the Odyssey and LOTR. Think an Odyssey Simulator.

There should be many different level types for you to interact with, providing a great
variety of challenges and problems to solve with brains or brawn as you continue your
journey, creating your own odyssey as you go.

The game takes inspiration from Brogue, Sil and DCSS, and aims to be simple and relatively
intuitive, while providing deep and rewarding functionality through the complex systems
synonymous with roguelikes. It currently uses an experience point system, although this
may change in the future.

Originally just a way for me to learn python, as it grew I decided to manage the project
properly and get it on GitHub. Any help/advice is greatly appreciated.

TO PLAY:
Download as a zip, extract into a folder of your choosing, and run firstrl.py.

CONTROLS:

Move with the numpad or arrow keys
Rest - Numpad 5
AutoRest - 'r'
Inventory - 'i'
Describe object - Right mouse click over tile to bring up description menu
Pick up - 'g'
Drop item - 'd'
Go down stairs - '>' or '.'
Character stats - 'c'

#Debug keys#
God mode - '@'
See all map - ']'
Heal player - '['
Damage player - '#'

MINOR TODO/BUGS:
#- Figure out how to stop stumbling from calling ai.take_turn().
#- get_player_effects and iterate_through_list seem to only
	want to show the first element of each list on the GUI.
#- Fix eat_food being called on map creation in weaponchances.py.
#- Add estimated time length to major todo list below.
#- Fix player_move_or_attack/play_game one of which seems to not be functioning correctly
	and returning their moved/stumbled string properly.
#- Fix this error that occurs occasionally on startup:

			File "firstrl.py", line 662, in is_blocked
				if map[x][y].blocked:
			IndexError: list index out of range

	I think it is because pygmys are trying to spawn beyond the wall/map.

#- Occasional error:

			File "weaponchances.py", line 493, in create_item
    		objects.append(item)
			UnboundLocalError: local variable 'item' referenced before assignment

#- Figure out how to get fatal effect warning to display, line 535.
#- Not sure if wander randomly works.
#-


MAJOR TODO (in rough order):
#- Break up firstrl.py into modules
#- Turn system
#- Fighter speed system
#- Add monster drops based on difficulty, to encourage risk/reward
#- Release a playable alpha
#- Scent tracking
#- Mutations/Godly powers
#- Click-to-path for map and GUI
#- New level types (forest, swamp, mountain range, meadow)
#- Quest system
#- Shift-heal, shift-run
#- Auto-explore
#- Graphical overhaul (possibly tileset)
#- High score page
#- Add all descriptions
#- Add danger_evaluate function for describe feature
#- Add ranged combat
#- Add more content (weapons/items/effects/monsters)
#- Add random generators for items and weapons
#- Improve monster pathfinding, will probably require path function.
#- Stealth system
#- Puzzles(?)
#- armor/skin/muscle/attack type simulation


DONE:
#- Fixed snake poison bug where the effect would be applied to the player and all snakes in FOV.
	Nested the check_for_poison function in the attack function. Probably should have been
	there in the first place. May be a similar bug in the eat_food() function.
#- Implemented singular boss system (will do for now)
#- Implemented message_wait system for discoveries the player needs to pay attention to.
#- Implemented (and fixed!) describe feature
#- Implemented hunger system. Food still buggy so only one type right now.
#- Implemented (and fixed!) Effects feature
#- Implemented wait for space key feature
#- Gave monsters (more or less) proper pathfinding.
#- Implemented space to continue function for scroll messages
#- A see all map debug key
#- Created singular special room function, but is not seperated from the map because v+h_tunnel does not check for intersection
#- Implemented evasion! Took like 5 minutes.
#- Added accuracy roll, a min/max system.
#- Added a new GUI to the right, displays monster.fighter hp bars when in FOV
#- Added character info box to panel2, discarded irrelevant/duplicated information like xp.



