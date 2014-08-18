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

The game takes inspiration from Brogue, Sil, Angband and DCSS, and aims to be simple and relatively
intuitive, while providing deep and rewarding functionality through the complex systems
synonymous with roguelikes(such as combat, effects, speed and random generation). It currently uses 
an experience point system, although this may change in the future.

Originally just a way for me to learn python, as it grew I decided to manage the project
properly and get it on GitHub. Any help/advice is greatly appreciated.

#To play:

Download as a zip, extract into a folder of your choosing, and run firstrl.py.
You will need to have Python 2.7 installed.

#Controls:

Move with the numpad or arrow keys

Rest a turn - Numpad 5

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

Damage player 10 hit points - '#'

#Features:

- Hunger and food system
- Scrolls, potions
- Effects (poison, confuse, paralyze etc)
- Evasion/accuracy/critical strike system
- Autorest
- Flash damage on hit
- Godly mutations

#Features TODO:

- Mouse to path
- Autoexplore/Shift run
- Turn system
- Speed system
- Scent tracking

#Minor TODO/bugs:

- Finish lever object
- Remove todo list from firstrl.py
- Bones and fountains appear over objects
- Rough balancing
- Change cast_fireball to apply a burning effect to all inside range for 5 turns. 
- Add gui bar for eff in monster.effects to display effects like burning, poisoned, confused, paralysed.
- Paralyze still lets you hit first few turns 
- Paralyze is tripled when lightning goes off and you are paralyzed
- Poison is being appended more than once. Something in add_effect() or roll_for_effect(). Debug it.
- Fix effect double append, highlighted lines both fire, although maybe not in the same run.
- Geting an occasional "ValueError: list.remove(x): x not in list" error after check_run_effects().
- Problem with warhammer splatter and lightning mutationmaknig it not fire
- Make bottom right box display info under mouse on mouse over
   
#Alpha TODO:

For alpha release:
    
    - MAJOR: Implement numdice*numfaces rolling system a la sil for attack. 
        (2 days - Will need to change attack, defense, ev, acc)
    - Add more items/weapons
        (2 days - After num*dice change, this will require a complete rework
    - MAJOR: Turn system http://www.roguebasin.com/index.php?title=A_simple_turn_scheduling_system_--_Python_implementation
        (3 days - Will probably require serious restructuring)
    - MAJOR: Implement speed via angbands method here: http://journal.stuffwithstuff.com/2014/07/15/a-turn-based-game-loop/
        (1 day - Probably not too bad as only adding a function here)
    - Fix current bugs: paralysis/poison duplication, paralyze taking a turn to 
        apply (move to different loop), bones/fountains cover items, warhammer 
        splatter not firing with elec.
        (3 days - One for each day as these have been difficult to pin down)
    - Move monster gen to new file and add enough monsters for 10-15 levels
        (1 day - Simple enough)
    - Add 2 more mutations
        (2 days - 1 for each as still no ideas, look at sil's abilities for inspiration)
    - Create 'forget map' effect
        (0.5 days - Seems simple enough)
    - Create 'blind' effect
        (0.5 days - Simple again)
    - Create 'burning' effect
        (0.5 days - Simple, every turn set a random orange colour too)
    - Add ranged combat if not too complex. Will need to integrate a render_all call for
        for each tile from attacker to target to paint an 'arrow' and display it once.
        Some internet time will be necessary to research.
        (3 days - Allow for 3 days to integrate this, research will give better estimates.
    - Add simple win condition for alpha release purposes
        (2 days - Will need to create win_screen() on win.)
    
    ALPHA UPDATE:
    19/08/14 (started countdown):    
        TOTAL DAYS = 20.5 (21)
        ALPHA RELEASE DATE = 9th September
        
#Remaining major TODO (in rough order):

- Noise effect/Color variation in tiles; first time map is created they should be set
- Shift-run (if next.x,y is not_blocked() and no fighter is in fov, take next step)
- Add click messages to see page of messages, rather than delete them, 
    append them to a new list, to be displayed on click + current game_msgs
- Add objects x 3/5/1 in inventory and floor
- Break up firstrl.py into modules, move modules that are called for by weaponchances
    into new files as directed from reddit post.
- Scent tracking
- Mutations/Godly powers
- Click-to-path for map and GUI
- Save maps and add upward stairs.
- New level types (forest, swamp, mountain range, meadow, hell)
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
- Add knockout effect for sneaking up on enemies
- Puzzles(?)
- Armor/skin/muscle/attack type simulation
- Add skills a la sil
- Implement some of sil's approach to skills and levels. 
- Add more food types (so far; feta, bread)
- Add a slice in half effect that colours squares directly beihnd the enemy red. By subtracting
    monster.x and y from player.x and y and figuring out which changed and in which direction 
    (+ or -) and rolling for a number of squares and if not blocked to paint those squares.
- Monster drops
- Add potion random names
- Add monster drops based on difficulty, to encourage risk/reward
- Figure out how to get fatal effect warning to display on panel2, line 535.

#Done:
- Made critical hits a function of accuracy
- Added borders and fixed character info to display iterative lists
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