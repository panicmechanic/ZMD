![Splash screen][splash]

###Zeus must die - A python roguelike based on the libtcod tutorial.

Originally just a way for me to learn python, as it grew I decided to manage the project
properly and get it on GitHub. Any help/advice is greatly appreciated.

###About:

An ancient Greece themed roguelike based on the weak premise that Zeus has gone mad and 
 done something so terrible it hath wrought the player out of his mastubatory mansion to claim his revenge.

The game itself will be familiar to roguelike-fans, hopefully not too much will need explaining, kill Zeus 
 and don't die. The game's mission statement is available [here][].
 
Pictures and gifs [here.][]
 
Updates several times a week, new .exe builds will be uploaded if and when I want to.

![screen][]
###To play:

####If you want the .exe (most people):

[Click here to download][], extract to a location of your choice and double click ZMD.exe inside the folder 'dist' to play.

####If you have Python 2.7 installed (python developers:

Download as a zip, extract into a folder of your choosing, and run firstrl.py.

You will need to have Python 2.7 installed.

###Controls:

Move with the numpad or arrow keys

Rest a turn - Numpad 5

Sprint - Alt + any directional key

AutoRest - Alt + '5' or 'r'

Inventory - 'i'

Describe object - Right mouse click over tile to bring up description menu

Pick up - 'g'

Drop item - 'd'

Go down stairs - '>'

Character stats - 'c'

Use godly powers - 'a'

###Features:

- 10 levels of macedonian mayhem
- 1 bearded god
- More than 50 weapons/items
- Almost(!) 15 monsters
- Hunger and food system
- Scrolls, potions
- Monster AI and pathfinding that doesn't make you want to die
- Effects (poison, confuse, paralyze etc)
- Dice/faces rolling system
- Evasion/accuracy/critical strike system
- Autorest
- Skills:
    
        Calisthenics (strength)  - Increases attack 
        Gymnastics (dexterity)   - Increase acc/ev 
        Shadow training (stealth)- Currently does nothing
        Meditation (will)        - Currently does nothing

- Godly mutations
- Speed system
- Alt-run
- [A pretty torch][here.]
- Fast progress!

![Progress][beforeafter]

###Mission statement:

ZMD is a roguelike in which you play an ancient Greek gladiator, hunting a beserk Zeus.
You seek retribution and will have to journey to the top of Mount Olympus to claim your
prize. On the way you will encounter many different randomised level types; forests,
dungeons, the sea of the dead and the infamous Mt. Olympus. You will have to outwit
great foes, avoid traps, solve puzzles, gather legendary items and battle mythic monsters.

The game seeks to (eventually) have a focus on combat, with tight mechanics and realisism.
The game should be short, around 3-5 hours to win, but have enough breadth and depth to keep
the player from acheiving mastery easily. It should include bonus levels with a similar mechanic to
DCSS's wings.

There should be many different level types for you to interact with, providing a great
variety of challenges and problems to solve with brains or brawn as you continue your
journey. There should be 10 levels, the first 5(?) randomised terrain, the last 5(?) ascending Mt. Olympus.

Repetitive tasks (such as grinding) should be kept to a minimum, including those necessary
to cross the dungeon, hot keys like fire/grab/open should be less than 5 and ideally use 
a universal hotkey system.

The game takes inspiration from Brogue, Sil, Angband and DCSS, and aims to be simple and relatively
intuitive, while providing deep and rewarding functionality through the complex systems
synonymous with roguelikes(such as combat, effects, speed and random generation). It currently uses 
an experience point system, although this may change in the future.

##Media:

![prettytorch][] 

![aresroar][]

###TODO:

- There are currently 2 critical bugs; one related to save_game trying to save map and running out 

    of memory and the other is fov_recompute causing a windows access error

###Done:

- Added prefabbed maps
- Added debug keys to show blocked tiles, and paths.
- Added skills, currently:

            2 strength = +1 power face.
            5 strength = +1 accuracy die
            1 dexterity = +1 ev +1 acc
            stealth = Nothing (no stealth system)
            will = Nothing (no alert/sleeping system)
            
- Fixed effects duplication bug
- Added shift_run
- Lerping updated, Only accepts a range of a single color at the moment, rather than two colors. Could be neater.
- Added wall/foor character foreground lerp
- Fixed monster color flash tiles outside fov by removing object.clear() call in main loop after display_dmg
- Added background color lerp to wall and floor color on init 
- Implemented flicker
- Added perlin noise to floor with non_working flicker
- Fixed monster pathfinding by setting current tile to blocked after moved 
- Added dice/faces random generation, integrated into attack, defense, evasion, accuracy.
 
    Affected by effects, equipment, crit roll and base levels. 
- Fixed player_rest() to print full health message instead of already healthy message
- Changed player colour
- Gave wall and floor tiles a character
- Added color player red when damaged
- Implemented speed
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
- Added accuracy roll, a min/max system6.
- Added a new GUI to the right, displays monster.fighter hp bars when in FOV
- Added character info box to panel2, discarded irrelevant/duplicated information like xp.


##Beyond here lies nothing useful.

####Alpha Schedule (now finished and kept for posterity):

For alpha release:
    
    - MAJOR: Implement numdice*numfaces rolling system a la sil for attack. 
        (DONE - 1 DAY. Still need to change old monster values)
    - Implement 4 skills above
        (DONE - After num*dice change, this will require a complete rework
    - MAJOR: Turn system http://www.roguebasin.com/index.php?title=A_simple_turn_scheduling_system_--_Python_implementation
        (DONE - 1.5 HOURS)
    - Implement shift run
        (DONE - Not too bad, needs more conditions)
    - Fix current bugs: None
        (DONE - All fixed.)
    - Move monster gen to new file and add enough monsters for 10 levels
        (DONE - Moved to new file, updated monsters + items with new attributes. Need to add more monsters
    - Add 1 more mutations
        (DONE - 1 for each as still no ideas, look at sil's abilities for inspiration and tomes abilities.
            Ideas:
            Hermes Timeslip - Doubles your speed for 10 turns (lvl1) ADDED
            Ares roar - Gives you an extra power die for 5 turns (lvl1) ADDED
            Apollo's Blessing - Doubles your stealth for 200 turns (lvl1)
            How to order these without having ten keys? A single key that brings up a menu if more than one is charged?
            Should change the torch color for some of these "Your torch glows red.."
    - Create 'forget map' effect
        (DONE - working)
    - Create 'blind' effect
        (DONE - working)
    - Create 'burning' effect
        (0 days - Pushed back to after alpha)
    - Add ranged combat if not too complex. 
        (0 days - Too complex before alpha, planned out in scrapbook.py.)
    - Implement pathfinding fix
        (DONE - Was a couple of mistakes in path_func.)
    - Add simple win condition for alpha release purposes
        (DONE - Simple win_screen and death condition for when I put a zeus monster on the map.
    - Clear out minor bugs above and playtest:
        (1 day) Bugs cleared.
    
    ALPHA UPDATE:
    19/08/14 (started countdown):    
        TOTAL DAYS LEFT = 22.5 (23)
        ALPHA RELEASE DATE = 11th September
    
    20/08/14 Finished speed, dice roll implementation, way ahead of schedule. But added pathfinding
                to TODO, as it breaks enjoyment and needs fixing if it's to be enjoyable in any way.
                Also fixed bones/fountains covering items and made both always_visible:    
        TOTAL DAYS LEFT = 16.5 (17)
        ALPHA RELEASE DATE = 6th September
        
    20/08/14 Fixed pathfinding. Added lerp to tiles, wasn't in TODO but vastly improves aesthetics. 
                Added shift run (now left alt run), most tasks have been easier than expected.                
        TOTAL DAYS LEFT = 12.5 (13)
        ALPHA RELEASE DATE = 3rd September
            
    21/08/14 Fixed effect duplication bug, was due to else statement being in wrong indentation.
                There was no paralyze issue.
        TOTAL DAYS LEFT = 11.5 (12)
        ALPHA RELEASE DATE = 2nd September
        
    26/08/14 Minor stuff done, slowed down a bit as pathfinding has been a pain in the ass and is not fixed. 
                Added forget_map effect.
        TOTAL DAYS LEFT = 11 (11)
        ALPHA RELEASE DATE = 6th September
    
    27/08/14 Added blind effect, tested that and forget map effect, both work fine. Removed but planned for ranged combat,
                as it is needs cascading changes while pathfinding continues to sprawl out it is better to get pathing 
                fixed and worry about ranged combat later, especially as ranged combat will eventually need pathfinding
                for monster AI.
                Added skills (strength, dex, stealth + will), added @property's for all. Implemented them into level up.
                Made strength and dex affect acc/ev/power                               
        TOTAL DAYS LEFT = 7.5 (8)
        ALPHA RELEASE DATE = 4th September
        
    28/08/14 Pathfinding is almost fixed, one bug still exists, but is too severe to ignore so work continues. Also 
                added debug keys for seeing blocked and pathed tiles. Fixed warhammer elec bug.
                Revamped torch for mutations tomorrow. Changed mutation effect attributes to be non specific.                
        TOTAL DAYS LEFT = 6.5 (7)
        ALPHA RELEASE DATE = 4th September
        
    30/08/14 Created monsterchances.py, updated monsters and item in weaponchances.py with new attributes.
                Still need to add more monsters. Pathfinding was fixed (almost entirely this time!).                    
        TOTAL DAYS LEFT = 4.5 (5)
        ALPHA RELEASE DATE = 5th September
        
    31/08/14 Added hermes timeslip mutation and Ares roar, working on creating systems necessary to support 
                passive/active mutations, will need an effect attribute to specify which. 
                Also made torch color change with ares roar, will be useful for illustrating effects clearly.                
        TOTAL DAYS LEFT = 2.5 (3)
        ALPHA RELEASE DATE = 3rd September
    
    01/09/14 Add new function to make_map to allow it to handle prefabricated maps. Still need to create Zeus, and win screen on his death_function.
                Finished a very simple win screen. Just need to add it to a zeus monster on the final level.
                Win_screen is bugged.                
                NEED TO DO PATHING!
        TOTAL DAYS LEFT = 1 (1)
        ALPHA RELEASE DATE = 2nd September
        
    02/09/14 Fixed win_screen to something simpler. Just need to do some playtesting and fix bugs, couple days.
        TOTAL DAYS LEFT = 2 (2)
        ALPHA RELEASE DATE = 4th September
    
    03/09/14 Fixed most bugs. Just some playtesting now
        TOTAL DAYS LEFT = 1 (1)
        ALPHA RELEASE DATE = 4th September
        
     
    
 

[splash]: http://i.imgur.com/XvWxZTB.png
[Click here to download]: https://github.com/panicmechanic/ZMD/releases
[here]: https://github.com/panicmechanic/ZMD#mission-statement
[beforeafter]: http://i.imgur.com/NoJgaX5.png
[prettytorch]: http://i.imgur.com/OXcnCeo.png
[aresroar]: http://imgur.com/VBmyMqy.png
[here.]: https://github.com/panicmechanic/ZMD#media
[screen]: http://i.imgur.com/7j6seun.png
