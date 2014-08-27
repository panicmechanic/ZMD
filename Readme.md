#Zeus must die - A python roguelike based on the libtcod tutorial.

Originally just a way for me to learn python, as it grew I decided to manage the project
properly and get it on GitHub. Any help/advice is greatly appreciated.

#To play:

Download as a zip, extract into a folder of your choosing, and run firstrl.py.
You will need to have Python 2.7 installed.

#Controls:

Move with the numpad or arrow keys

Rest a turn - Numpad 5

Sprint - Alt + any directional key

AutoRest - Alt + '5' or 'r'

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
- Rough balancing
- Change cast_fireball to apply a burning effect to all inside range for 5 turns. 
- Add gui bar for eff in monster.effects to display effects like burning, poisoned, confused, paralysed.

- Problem with warhammer splatter and lightning mutation making it not fire - give take_damage another variable, weapon.
 
    If it is war hammer, and the damage will kill the monster, give it the splatter effect in a function.
- Make bottom right box display info under mouse on mouse over
- Give all monsters a speed and heal_rate
- Stun effect
- Give an @property value to speed, accuracy, evasion
- Implement stealth by giving fighters a detection and stealth value 
- Give fighters an awareness value equal to sleeping, wandering, aware. If monster is in fov and distance < 10
 
    roll stealth/detection and raise awareness 1 level. While sleeping cannot wander.
    
- Fix name_stat_gen() and make iterate_through_list() print each item with auto wrap.      

- Still some minor bugs to iron out to roll, level up needs changing which will probably require adding the following:

        Skills (set default speed to 100):
    
        Calisthenics (strength)  - Increase attack (power sides by 1), increase ranged range. 
        Gymnastics (dexterity)   - Increase acc/ev, small boost to speed
        Shadow training (stealth)- Improve stealth, defense improve speed
        Meditation (will)        - Improve accuracy, perception checks, skill helps mutations
              
- Fix pathing to walk as close as possible if in fov and path is blocked.***
- Torch colours and back/fore colours are still not displayed right, check all values.
- Figure out how to make color_flash work
- Add description to box with auto wrap
- Give description window and character/level up window borders.

- go_to_last_seen functionality is broken.    
- Make inventory a combination of equipped and other inventory
- Move passable set from monster_move_or_attack() to move()
- Create an extra map to store pathfinding in without monster blocks.
- Add an effect to increase stealth for every adjacent wall to player - sneaking    

#Alpha TODO:

For alpha release:
    
    - MAJOR: Implement numdice*numfaces rolling system a la sil for attack. 
        (DONE - 1 DAY. Still need to change old monster values)
    - Add more items/weapons, implement 4 skills above
        (1 day - After num*dice change, this will require a complete rework
    - MAJOR: Turn system http://www.roguebasin.com/index.php?title=A_simple_turn_scheduling_system_--_Python_implementation
        (DONE - 1.5 HOURS)
    - Implement shift run
        (DONE - Not too bad, needs more conditions)
    - Fix current bugs: Warhammer splatter not firing with elec.
        (1 days - One for each day as these have been difficult to pin down)
    - Move monster gen to new file and add enough monsters for 10 levels
        (1 day - Simple enough)
    - Add 2 more mutations
        (2 days - 1 for each as still no ideas, look at sil's abilities for inspiration and tomes abilities.)
    - Create 'forget map' effect
        (DONE - working)
    - Create 'blind' effect
        DONE - working)
    - Create 'burning' effect
        (0.5 days - Simple, every turn set a random orange colour too)
    - Add ranged combat if not too complex. 
        (0 days - Too complex before alpha, planned out in scrapbook.py.)
    - Implement pathfinding fix
        (IN PROGRESS - Decided to implement callbacks into pathfinding for future ease, but proving difficult. Ongoing.
    - Add simple win condition for alpha release purposes
        (2 days - Will need to create win_screen() on win, make dungeon depth 10 levels, lerp wall/floor color each level to get darker/lighter.)
    
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
    
    26/08/14 Added blind effect, tested that and forget map effect, both work fine. Removed but planned for ranged combat,
                as it is needs cascading changes while pathfinding continues to sprawl out it is better to get pathing 
                fixed and worry about ranged combat later, especially as ranged combat will eventually need pathfinding.
                for monster AI.
                Added skills (strength, dex, stealth + will), added @property's for all. Implemented them into level up.
                Made strength give you an extra power face for every two points.                
        TOTAL DAYS LEFT = 7.5 (8)
        ALPHA RELEASE DATE = 4th September
        
    
        
#Remaining major TODO (in rough order):

- Would be really cool to find thematic ways to give the player chances to train. This could remove the need for xp entirely.
    
    E.g you are captured by harpies, after disptaching them you save a prisoner who offers you a special type of 
    
    training, boosting your stats much more than a level up. Maybe giving you a mutation too.
- Need a fire key for mutations, and a box to list available mutations that are charged and ready to fire
- Place items in clusters, define level of clusters pwr dungeon level
- Fix description box by putting it in panel2 and include a new function to describe acc, speed, danger etc.
- Pathfinding will need an overhaul
- Add variables to tiles at the entrances and exits to tunnels, and on entering 
    
    new rooms, and if map[x][y].run_block == True stop the shift_run. Will need to change
    the make_map function.
- Make inventory a list in the fighter class so monsters can have them.
- Make monsters drop items in inventory based on a roll from inventory but use system like other 
- Fix pathfinding- look at example code in library.
- Describe item in inventory feature
- As it is common to find multiples of the same item there needs to either be variation in those items or a degradation quality to the items
- Noise effect/Color variation in tiles; first time map is created they should be set
- Shift-run (if next.x,y is not_blocked() and no fighter is in fov, take next step)
- Add click messages to see page of messages, rather than delete them, 
    append them to a new list, to be displayed on click + current game_msgs
- Add objects x 3/5/1 in inventory and floor
- Break up firstrl.py into modules, move modules that are called for by weaponchances
    into new files as directed from reddit post.
- Scent tracking~
- Mutations/Godly powers
- Click-to-path for map and GUI
- Save maps and add upward stairs.
- New level types (forest, swamp, mountain range, meadow, hell)
- Quest system
- Auto-explore
- Stop time ability
- Graphical overhaul (possibly tileset)
- High score page (start in player_death())
- Add all descriptions
- Add danger_evaluate function for describe feature
- Add ranged combat
- Add more content (weapons/items/effects/monsters)
- Add random generators for items and weapons
- Check FPS
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
- Add big halls with many, many drinking foes, as a challenge to players stealth.
- Use cellular automata for mountains and forests, 2nd3rd image here: http://www.gridsagegames.com/blog/2014/06/mapgen-cellular-automata/
- Mutations should behave like abilities from sil, using collected xp points to purchase mutations.

    Should be many types of mutation (50+(?) and intereact with one-another for emergent gameplay.
    Aome should need prerequisite skill points in skills i.e. calisthenics etc.
- A dungeon generator capable of diffferent tpyes of layout, with post processing. Look here for ideas, seclusion analytics could place rarer objects.
- After alpha, take some time to consider gameplay and innovation. Set goals for 0.1.0. 
Make monster drops a chance of a next level item, build an anticipation. http://journal.stuffwithstuff.com/2014/07/05/dropping-loot/s
- Consider combat:

        ..each type of weapon (sixteen total, four each in four categories, short/long/heavy/slashing) will have a
        "moveset" like a Dark Souls weapon. 
        The closest thing I've seen similar to date are the moves from Sword in Hand[1] - if you look on the right of
        the bar it shows what'll be attacked by each move and how (it at all) the player will move. In URR most moves 
        will be available just by acquiring the weapon, a small number for each weapon can be learned. The combat system
        is going to be heavily focused on the timing of moves, the area they do damage in, whether they do damage
        high/mid/low (i.e. head/torso/legs), and how many turns they take, whether your enemy has their shield 
        up/lowered, etc. The other inspiration is FTL. I've always enjoyed the way that depending on the situation, 
        different parts of the enemy ship - shields, weapons, engines, etc - are the appropriate first target. I want to
        make it so that you want to assess your enemy at the start of battle - what weapon do they have, what kind of 
        shield, do they have a helmet, cuirass, etc - and then use that, and how fast/slow you know they'll be with 
        their weapon, and your knowledge of your weapon/armour, to figure out a timing process of blocking, attacking,
        and attacking their weakest points.
        
        Additional edit: The intention is to be akin to Dark Souls in another way - with "perfect play" you should
        be able to escape from a 1v1 damage-free, but on a 2v1 or more you'll have to think about positioning, items,
        other factors, etc.
        
        [1] - http://www.zincland.com/7drl/sword/
- Look here: http://www.reddit.com/r/roguelikes/comments/2bsa6x/describe_your_perfect_roguelike/
    
    /Being able to strangle an elf with a wombat leather sock from it's own severed foot. 
    
    /Casting Polymorph Arm to Banana followed by Animate Banana and watching a goblin's own arm beat it to death.
    
- Play TGGW/Cave of Qud/Cataclysm for 'research'
- Random quest element - As walknig through a forest you are suddenly messaged that you have been captured and a 
    
    new level loads, from here any type of quest could play out.
- Maybe you steal powers from the gods and they have all gone mad?   
- Look at p&p systems: http://www.reddit.com/r/roguelikedev/comments/2ecmrs/sharing_saturday_12/ck0m8lg
- Monster fear/alertness/sleeping
- Monsters should all be able to have effects, ranged attacks and special moves (functions that do not fall under effects)

    although perhaps it would be easier to make effects find a way to test for the right conditions (nested in the effect) and if true, use it.
- From /u/munificent: 

        If it doesn't have a move to use, it needs to decide how it's going to harm the player. It has two options: it 
        can try to get close and do a melee attack or (if it has any ranged attacks), it can try to do a ranged attack. 
        Getting this working was the hardest part of the AI, but when I did, it made a huge difference in how smart the 
        monsters seem.

- In fact, just read his whole post regarding ai: http://www.reddit.com/r/roguelikedev/comments/2en9jh/weekly_wednesday_systems_sharing_1_ai_systems/ck1uttn


#Done:

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


#Mission statement:



ZMD is a roguelike in which you play an ancient Greek gladiator, hunting a beserk Zeus.
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
