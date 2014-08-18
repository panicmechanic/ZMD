#Zeus must die - A python roguelike based on the libtcod tutorial.

#Mission statement:

ZMD is a roguelike in which you play an ancient Greek gladiator, hunting a bezerk Zeus.
You seek retribution and will have to journey to the top of Mount Olympus to claim your
prize. On the way you will encounter many different randomised level types; forests,
dungeons, the sea of the dead and the infamous Mt. Olympus. You will have to outwit
great foes, avoid traps, solve puzzles, gather legendary items and battle mythic monsters.

The game seeks to (eventually) have a feeling of undertaking a great journey, different
every time you play. As inspired by the Odyssey and LOTR. Think an Odyssey Simulator.

There should be many different level types for you to interact with, providing a great
variety of challenges and problems to solve with brains or brawn as you continue your
journey, creating your own odyssey as you go.

Repetitive tasks (such as grinding) should be kept to a minimum, including those necessary
to cross the dungeon, hot keys like fire/grab/open should be less than 5 and ideally use 
a universal hotkey system.

The game takes inspiration from Brogue, Sil and DCSS, and aims to be simple and relatively
intuitive, while providing deep and rewarding functionality through the complex systems
synonymous with roguelikes(such as combat). It currently uses an experience point system, 
although this may change in the future.

Originally just a way for me to learn python, as it grew I decided to manage the project
properly and get it on GitHub. Any help/advice is greatly appreciated.

#To play:
Download as a zip, extract into a folder of your choosing, and run firstrl.py.

#Controls:

Move with the numpad or arrow keys

Rest - Numpad 5

AutoRest - 'r'

Inventory - 'i'

Describe object - Right mouse click over tile to bring up description menu

Pick up - 'g'

Drop item - 'd'

Go down stairs - '>' or '.'

Character stats - 'c'

#Debug keys:

God mode - '@'

See all map - ']'

Heal player - '['

Damage player - '#'

#Features:
(- = TODO)

- Hunger and food system
- Scrolls, potions
- Effects (poison, confuse, paralyze etc)
- Evasion/accuracy/critical strike system
- Autorest
- Flash damage on hit
- Mouse to path-
- Autoexplore-
- Turn system-
- Scent tracking-


#Minor TODO/bugs:

- get_player_effects and iterate_through_list seem to only
	want to show the first element of each list on the GUI.	
    Put 2 new boxes with equipped items and effects iterated and displayed with \n.
- Add estimated time length to major todo list below.
- Figure out how to get fatal effect warning to display on panel2, line 535.
- Finish lever object
- Have evasion and accuracy both draw their values from a new fighter variable 'dex'.
- Add more food types (so far; feta, bread)
- Remove todo list from fristrl.py
- Bones and fountains appear over objects
- Rough balancing
- Use color more sparingly, change any important messages to white
- Change cast_fireball to apply a burning effect to all inside range for 5 turns. 
- Add gui bar for eff in monster.effects to display effects like burning, poisoned, confused, paralysed.
- Paralyze still lets you hit first few turns 
- Paralyze is tripled when lightning goes off and you are paralyzed
- Poison is being appended more than once. Something in add_effect() or roll_for_effect(). Debug it.
- Add a slice in half effect that colours squares directly beihnd the enemy red. By subtracting
    monster.x and y from player.x and y and figuring out which changed and in which direction 
    (+ or -) and rolling for a number of squares and if not blocked to paint those squares.
- Fix effect double append, highlighted lines both fire, although maybe not in the same run.
- Geting an occasional "ValueError: list.remove(x): x not in list" error after check_run_effects().
- Shift-run
- Problem with warhammer splatter and lightning mutation
- Add knockout effect for sneaking up on enemies
   
#Major TODO (in rough order):
- Create 'Forget map' effect
- Create 'blind' effect
- Make critical hits a function of accuracy roll and evasion roll (a la sil)
- Implement numdice*numfaces rolling system a la sil for attack.
- Break up firstrl.py into modules
- Turn system
- Fighter speed system
- Add potion random names
- Add objects x 3/5/1 in inventory and floor
- Add more attack type effects like explode.
- Add monster drops based on difficulty, to encourage risk/reward
- Improve GUI. Maybe a border.
- Add click messages to see page of messages, rather than delete them, 
    append them to a new list, to be displayed on click + current game_msgs
- Release a playable alpha
- Scent tracking
- Mutations/Godly powers
- Click-to-path for map and GUI
- Save maps and add upward stairs.
- New level types (forest, swamp, mountain range, meadow)
- Quest system
- Auto-explore
- Graphical overhaul (possibly tileset)
- High score page (start in player_death())
- Add all descriptions
- Add danger_evaluate function for describe feature
- Add ranged combat
- Add more content (weapons/items/effects/monsters)
- Add random generators for items and weapons
- Improve monster pathfinding, will probably require path function. Also need to fix path to last seen.
- Reduce evasion by 1 for every adjacent monster
- Create a jelly_monster that splits when hit.
- Stealth system, via angbands monster alertness level, perception score and players stealth roll.
- Puzzles(?)
- Armor/skin/muscle/attack type simulation
- Not happy with add/ev character level up, too much choice. Maybe just give player a random stat
    and boost acc and ev by 2.
- Implement some of sil's approach to skills and levels. 

#Done:
- Made msgs background black with new console "msgs"
- Added colour range for damage flash based on severity of damage.
- Added display damage on hit!
- Added mutations, currently a little buggy.
- Added paralyze effect and gave it to fireflys.
- Added critical hits for player, currently hidden from monsters.
- Made damage in attack vary blow by blow by including "acc_roll-ev_roll + power-defense"
    also added a stain floor with blood, but needs to be rarer/removed entirely.
- Added a monster_death explode function for aesthetics. Currently fires when player wields warhammers.
- Fixed monster pathfinding to last seen location, fixed load functionality, created monster_move_or_attack
- Added hunger bar, fixed eat_food() to not exceed 800. 800 should probably be a global value.
- Fixed check_run_effects to properly remove effects, display them correctly. Also made 
    function message player when lethal effect is no longer true.
- Fixed check_run_effects to reset turns_passed to 0 when effect is removed.
- Added roll_for_effect to allow fighters to apply an effect to another fighter.
- Added poison bar, moved dungeon level to char info
- Fixed eat_food being called every map gen, also fixed eat_food by nesting it under Fighter class.
- Fixed stumbling
- Fixed player_move_or_attack and made sure handle_keys returns its value properly
- Fixed occasional startup error due to pygmys spawning outside the map
- Implemented Auto rest function, stops on 50, 80 and 100 hp. Will also stop if too hungry or monster in FOV.
- Fixed snake poison bug where the effect would be applied to the player and all snakes in FOV.
	Nested the check_for_poison function in the attack function. Probably should have been
	there in the first place. May be a similar bug in the eat_food() function.
- Implemented singular boss system (will do for now)
- Implemented message_wait system for discoveries the player needs to pay attention to.
- Implemented (and fixed!) describe feature
- Implemented hunger system. Food still buggy so only one type right now.
- Implemented (and fixed!) Effects feature
- Implemented wait for space key feature
- Gave monsters (more or less) proper pathfinding.
- Implemented space to continue function for scroll messages
- A see all map debug key
- Created singular special room function, but is not seperated from the map because v+h_tunnel does not check for intersection
- Implemented evasion! Took like 5 minutes.
- Added accuracy roll, a min/max system.
- Added a new GUI to the right, displays monster.fighter hp bars when in FOV
- Added character info box to panel2, discarded irrelevant/duplicated information like xp.