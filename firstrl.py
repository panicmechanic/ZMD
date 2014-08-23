import libtcodpy as libtcod
import math
import textwrap
import shelve
import weaponchances
import time
from weaponchances import create_item

# BORDER VARIABLES

BORDER_CORNER = chr(15)
BORDER_FILL = '+'
BORDER_COLOR = libtcod.gold
BORDER_BACKGROUND = libtcod.darkest_grey

#FATAL EFFECT
FATAL_EFFECT = False
FATAL_NAME = None


# actual size of the window
SCREEN_WIDTH = 130
SCREEN_HEIGHT = 60


#size of the map
MAP_WIDTH = 106
MAP_HEIGHT = 53

#parameters for dungeon generator
ROOM_MAX_SIZE = 12
ROOM_MIN_SIZE = 5
MAX_ROOMS = 55

#sizes and coordinates relevant for GUI
BAR_WIDTH = 20
PANEL_HEIGHT = 7

PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 1
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 1
MSG_HEIGHT = PANEL_HEIGHT - 1
INVENTORY_WIDTH = 50
LEVEL_SCREEN_WIDTH = 40
CHARACTER_SCREEN_WIDTH = 25
EFFECTS_GUI = 4

# PANEL 2
PANEL2_HEIGHT = SCREEN_HEIGHT
PANEL2_WIDTH = 24
RECT_HEIGHT = 16 - PANEL2_HEIGHT  # 16 being the max height of the enemy fov panel.
MSG_STOP = MSG_WIDTH - PANEL2_WIDTH
PANEL_WIDTH = SCREEN_WIDTH - PANEL2_WIDTH

#FOV
FOV_ALGO = 0  #Default FOV algorithm
FOV_LIGHT_WALLS = True  #Light walls or not

#Item parameters
HEAL_AMOUNT = 40
LIGHTNING_DAMAGE = 40
LIGHTNING_RANGE = 5
CONFUSE_NUM_TURNS = 10
CONFUSE_RANGE = 8
FIREBALL_RADIUS = 3
FIREBALL_DAMAGE = 25
HEAL_RATE = 1

#Food properties
HUNGER_RATE = 1
HUNGER_TOTAL = 8000
HUNGER_WARNING = 100
CURRENT_ATTACK = None

#Player parameters
LEVEL_UP_BASE = 200
LEVEL_UP_FACTOR = 200

#FPS
LIMIT_FPS = 60  #60 frames-per-second maximum

#Darkest wall can be when not in FOV
color_set_wall_dark = libtcod.darkest_grey
#Lightest wall can be when not in FOV, bottom for lerp
color_dark_wall = libtcod.darker_grey
#Top for lerp
color_light_wall = libtcod.Color(70, 70, 2)#Yellowed

#Darkest wall can be when not in FOV
color_char_set_dark_wall = libtcod.darker_grey
#Lightest, unused
color_char_dark_wall = libtcod.dark_grey
#Top for lerp
color_char_light_wall = libtcod.Color(107, 107, 12)#Yellowed



color_set_ground_dark = libtcod.Color(50, 60, 40)
color_dark_ground = libtcod.Color(80, 90, 70)
color_light_ground = libtcod.Color(100, 100, 14)

color_char_set_dark_ground = libtcod.Color(80, 90, 70)
color_char_dark_ground = libtcod.Color(110, 110, 100)
color_char_light_ground = libtcod.Color(120, 120, 15)


WALL_CHAR = '#'
FLOOR_CHAR = '.'

TORCH_RADIUS = 8
SQUARED_TORCH_RADIUS = TORCH_RADIUS * TORCH_RADIUS
FOV_NOISE = None
FOV_TORCHX = 0.0
FOV_INIT = False
FOV_ALGO_NUM = 1
NOISE = libtcod.noise_new(1)



class Tile:
    # a tile of the map, and its properties
    def __init__(self, blocked, block_sight=None, diff_color=None, color_flash=None, color_set=None, color_fore=None):
        self.blocked = blocked
        self.diff_color = diff_color

        self.color_flash = color_flash
        self.color_set = color_set
        self.color_fore = color_fore

        #all tiles start unexplored
        self.explored = False

        #by default if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight


class Rect:
    #A rectangle on the map, used to characterise a room
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return (center_x, center_y)

    def intersect(self, other):
        #returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


class Object:
    #this is a generic object: the player, a monster, an item, the stairs...
    #it's always represented by a character on screen.
    def __init__(self, x, y, char, name, color, equipment=None, effects=None, blocks=False, always_visible=False,
                 fighter=None, ai=None, item=None, description=None, seen=False, path=None, decorative=False,
                 display_dmg=None):
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.color = color
        self.blocks = blocks
        self.always_visible = always_visible
        self.fighter = fighter
        if self.fighter:  #let the fighter component know who owns it
            self.fighter.owner = self

        self.ai = ai
        if self.ai:  #let the ai component know who owns it
            self.ai.owner = self

        self.item = item
        if self.item:  #let the item component know who owns it, like a bitch
            self.item.owner = self

        self.equipment = equipment
        if self.equipment:  #let the equipment component know who owns it
            self.equipment.owner = self

            #there must be an Item component for the Equipment component to work properly
            self.item = Item()
            self.item.owner = self

        self.effects = effects
        if self.effects:  #let the effect component know who owns it
            self.effects.owner = self

            #there must be a fighter component for the effect component to work properly
            self.fighter = Fighter()
            self.fighter.owner = self

        self.description = description
        self.seen = seen

        self.path = path

        self.decorative = decorative

        self.display_dmg = display_dmg

    def move(self, dx, dy):
        #move by the given amount, if the destination is not blocked
        if not is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy

    def move_towards(self, target_x, target_y):
        #A lot of this is taken directly from SevenTrials (https://github.com/nefD/SevenTrials)
        #and modified to work here.

        #This creates the path needed, in seven trials this is done in play_game loop,
        # load_game() and use() functions.

        if self.path is None:
            self.path = libtcod.path_new_using_map(fov_map)

        #Compute path to player
        libtcod.path_compute(self.path, self.x, self.y, target_x, target_y)

        #vector from this object to the target, and distance
        if not libtcod.path_is_empty(self.path):

            path_x, path_y = libtcod.path_get(self.path, 0)

            #normalise it to 1 length (preserving direction), then round it and
            #convert to integer so the movement is restricted to the map grid
            dx = path_x - self.x
            dy = path_y - self.y

        else:
            #TODO: Else, path as close as possible
            print 'Path is empty'
            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.sqrt(dx ** 2 + dy ** 2)
            dx = int(round(dx / distance))
            dy = int(round(dy / distance))

        self.move(dx, dy)

    def distance_to(self, other):
        #return the distance to another object
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance_from(self, x, y):
        # return the distance to another x,y coordinates
        dx = x - self.x
        dy = y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance(self, x, y):
        #return the distance to some coordinates
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def send_to_back(self):
        #make this object be drawn first, so all other appear above it if they're in the same tile.
        global objects
        objects.remove(self)
        objects.insert(0, self)

    def draw(self):

        #only show if it's visible to the player or it's set to always visible and on an explored tile
        if (libtcod.map_is_in_fov(fov_map, self.x, self.y) or (self.always_visible and map[self.x][self.y].explored)):
            #set the color and then draw the character that represents this object at its position
            libtcod.console_set_default_foreground(con, self.color)
            libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def clear(self):
        #erase the character that represents this object
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

    def describe(self, description):
        #describe this object
        if self.description is None:
            message('The ' + self.owner.name + ' cannot be described.')
        else:
            message(str(description), libtcod.white)


class Fighter:
    #combat-related properties and methods (monster, player, npc).
    def __init__(self, hp, defense_dice=0, defense_sides=0, power_dice=0, power_sides=0, evasion_dice=0, evasion_sides=0, accuracy_dice=0, accuracy_sides=0, crit_dice=0, xp=0, speed=None, speed_counter=0, heal_rate=50, heal_counter=0, death_function=None, effects=[], cast_effect=None, cast_roll=0, paralysis=False):
        self.base_max_hp = hp
        self.hp = hp
        self.base_defense_dice = defense_dice
        self.base_defense_sides = defense_sides
        self.base_power_dice = power_dice
        self.base_power_sides = power_sides
        self.base_evasion_dice = evasion_dice
        self.base_evasion_sides = evasion_sides
        self.base_accuracy_dice = accuracy_dice
        self.base_accuracy_sides = accuracy_sides
        self.crit_dice = crit_dice
        self.xp = xp
        self.speed = speed
        self.speed_counter = speed_counter

        #Standard of 50 means it will heal at the same rate as the player
        self.heal_rate = heal_rate
        self.heal_counter = heal_counter

        self.death_function = death_function
        self.effects = effects
        self.cast_effect = cast_effect
        self.cast_roll = cast_roll
        self.paralysis = paralysis


    @property
    def power(self):  #return actual power, by summing up the bonuses from all equipped items
        #Add dice/sides from equipment
        bonus_dice = (sum(equipment.power_bonus_dice for equipment in get_all_equipped(self.owner))+(self.base_power_dice)+(self.crit_dice))
        bonus_sides = (sum(equipment.power_bonus_sides for equipment in get_all_equipped(self.owner))+(self.base_power_sides))

        #Add dice/sides from effects
        bonus_dice += (sum(effect.power_effect_dice for effect in self.effects))
        bonus_sides += (sum(effect.power_effect_sides for effect in self.effects))

        #Create list with dice and sides as it's two entries
        dice_sides = []
        dice_sides.append(bonus_dice)
        dice_sides.append(bonus_sides)

        #Return the list
        return dice_sides

    @property
    def defense(self):  #return actual+ defense, by summing up the bonuses from all equipped items
        bonus_dice = (sum(equipment.defense_bonus_dice for equipment in get_all_equipped(self.owner))+(self.base_defense_dice))
        bonus_sides = (sum(equipment.defense_bonus_sides for equipment in get_all_equipped(self.owner))+(self.base_defense_sides))

        #Need to integrate effects below
        bonus_dice += (sum(effect.defense_effect_dice for effect in self.effects))
        bonus_sides += (sum(effect.defense_effect_sides for effect in self.effects))

        dice_sides = []
        dice_sides.append(bonus_dice)
        dice_sides.append(bonus_sides)

        return dice_sides

    @property
    def max_hp(self):  #return actual max_hp, by summing up the bonuses from all equipped items

        #This stays unaffected
        bonus = sum(equipment.max_hp_bonus for equipment in get_all_equipped(self.owner))
        #Add effect bonuses to max_hp
        bonus += (sum(effect.max_hp_effect for effect in self.effects))
        return self.base_max_hp + bonus


    @property
    def evasion(self): #return actual evasion
        bonus_dice = (sum(equipment.evasion_bonus_dice for equipment in get_all_equipped(self.owner))+(self.base_evasion_dice))
        bonus_sides = (sum(equipment.evasion_bonus_sides for equipment in get_all_equipped(self.owner))+(self.base_evasion_sides))

        #Need to integrate effects below
        bonus_dice += (sum(effect.evasion_effect_dice for effect in self.effects))
        bonus_sides += (sum(effect.evasion_effect_sides for effect in self.effects))

        dice_sides = []
        dice_sides.append(bonus_dice)
        dice_sides.append(bonus_sides)

        return dice_sides

    @property
    def accuracy(self): #return actual accuracy
        bonus_dice = (sum(equipment.accuracy_bonus_dice for equipment in get_all_equipped(self.owner))+(self.base_accuracy_dice))
        bonus_sides = (sum(equipment.accuracy_bonus_sides for equipment in get_all_equipped(self.owner))+(self.base_accuracy_sides))

        #Need to integrate effects below
        bonus_dice += (sum(effect.accuracy_effect_dice for effect in self.effects))
        bonus_sides += (sum(effect.accuracy_effect_sides for effect in self.effects))

        dice_sides = []
        dice_sides.append(bonus_dice)
        dice_sides.append(bonus_sides)

        return dice_sides

    def player_eat_food(self, Item):
        global hunger_level

        if hunger_level >= HUNGER_TOTAL - HUNGER_WARNING:
            message('You are already full!', libtcod.white)
        else:
            message('Mmm, that was delicious!', libtcod.light_green)
            if hunger_level + Item.food_value > HUNGER_TOTAL:
                hunger_level = HUNGER_TOTAL
            else:
                hunger_level += Item.food_value


    def add_effect(self, Effect, object_origin_name):  # Add effect to the fighter class's list of effects
        # check if the effect already exists, if it does, just increase the duration

        #if effects is not empty, iterate through them
        if self.effects != []:
            #create a variable to hold a statement that changes if the i.effectname is the same as the one already applied
            duplicate=False
            #Iterate through them
            for i in self.effects:
                #If an effect with the same name already exists and duplicate hasn't been changed, add its duration to the existing copy.
                if i.mutation == False and i.effect_name == Effect.effect_name and duplicate==False:
                    #Update variable to stop the iteration through self.effects, as we've found a copy already. This stops duplication.
                    duplicate=True
                    #Increase this effects duration rather than adding multiple effects, could be done either way but this is simpler.
                    i.duration += Effect.base_duration
                    #Increase the variable applied_times which is used in other functions like render_bar() to show how many times poison has been applied
                    i.applied_times += 1
                    #Tell the player what happened
                    message('The ' + object_origin_name + ' has ' + Effect.effect_name + ' you further!',
                            libtcod.white)

                elif i.mutation == True and i.effect_name == Effect.effect_name and Effect.mutation == True:
                    i.applied_times += 1
                    duplicate=True

                    message('The gods have blessed your ' + Effect.effect_name + ' further!',
                            libtcod.white)

            #Else, if a duplicate has not been found.
            if duplicate==False:
                #Add the effect
                self.effects.append(Effect)
                #Tell the play what happened
                message('The ' + object_origin_name + ' has ' + Effect.effect_name + ' you!', libtcod.yellow)

        elif Effect.mutation == True:
            self.effects.append(Effect)
            #Set duration to base duration
            Effect.duration = Effect.base_duration
            message(object_origin_name + ' ' + Effect.effect_name + '!' + ' Press space to continue.', libtcod.white)
            update_msgs()
            wait_for_spacekey()

        #Else, effects is empty and this effect is not a mutation, so just add it to the player and tell them what happened.
        else:
            self.effects.append(Effect)
            message('The ' + object_origin_name + ' has ' + Effect.effect_name + ' you!', libtcod.yellow)


    def remove_effect(self, Effect):
        if Effect.duration == Effect.turns_passed:

            Effect.applied_times = 1
            self.effects.remove(Effect)


    def take_damage(self, damage):
        global fov_recompute
        #apply damage if possible
        if damage > 0:
            self.hp -= damage

        #check for death, if there's a death function, call it.
        if self.hp <= 0:
            function = self.death_function
            if function is not None:
                function(self.owner)

            if self.owner != player:  #yield experience to the player
                player.fighter.xp += self.xp

        #Tell display_damage() in render_all() to fire on this tile
        self.owner.display_dmg = damage


    def attack(self, target):
        #a simple formula for attack damage

        evasion = roll_for(target.fighter.evasion)
        accuracy = roll_for(self.accuracy)

        #If evasion is smaller or equal to accuracy
        if evasion <= accuracy:

            #check for crit if player is the attacker
            if self.owner.name == 'player':

                difference = accuracy - evasion

                if difference >= 10:

                    #color the floor with blood
                    libtcod.console_set_char_background(con, target.x, target.y, libtcod.darker_red, libtcod.BKGND_SET)
                    map[target.x][target.y].diff_color = libtcod.darker_red
                    message('You deal a devastating critical blow to the ' + str(target.name) + '!', libtcod.white)

                    #Size of critical boost, later will roll for this damage
                    if difference >= 10:
                        self.crit_dice=1
                    elif difference <= 15:
                        self.crit_dice=2
                    elif difference <= 20:
                        self.crit_dice=3
                    elif difference <= 25:
                        self.crit_dice=4

            #Call rolls for power and defense
            power = roll_for(self.power)
            defense = roll_for(target.fighter.defense)

            #Set crit damage to 0 now that it has been calculated and stored in power variable
            self.crit_dice=0

            #Calculate damage
            damage = power - defense

            # #Player messages and colors##
            if damage > 0 and self.owner.name == 'player':
                #make the target take some damage and print the value
                message('You hit the ' + target.name + ' for ' + str(damage) + ' damage!', libtcod.green)
                target.fighter.take_damage(damage)

            elif damage <= 0 and self.owner.name == 'player':
                #else print a message about how puny you are
                message('You hit the ' + target.name + ' but it has no effect!', libtcod.grey)

            ##Monster messages and colors##
            elif damage > 0 and self.owner.name != 'player':
                #make the target take some damage and print the value
                message(self.owner.name.capitalize() + ' hit you for ' + str(damage) + ' damage!', libtcod.red)
                target.fighter.take_damage(damage)
                self.roll_for_effect(target)

            elif damage <= 0 and self.owner.name != 'player':
                message(self.owner.name.capitalize() + ' hits you but it has no effect!', libtcod.grey)
                self.roll_for_effect(target)

        elif self.owner.name == 'player' and evasion > accuracy:
            message('You missed the ' + target.name + '!', libtcod.white)

        elif self.owner.name != 'player' and evasion > accuracy:
            message('The ' + self.owner.name.capitalize() + ' missed you!', libtcod.white)

        quality_string = None
        damage = 0


    # check for auto cast_effect
    def roll_for_effect(self, target):
        #if the fighter has an effect to be cast, and the roll is > cast_roll - add effect to target.
        roll = libtcod.random_get_int(0, 0, 100)
        if self.cast_effect != None and roll <= self.cast_roll:
            target.fighter.add_effect(self.cast_effect, self.owner.name)


    def heal(self, amount):
        #heal by the given amount, without going over the maximum
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp


class BasicMonsterAI:
    global path
    #AI for a basic monster.
    def take_turn(self):

        #A basic monster takes its turn. If you can see it, it can see you.
        monster = self.owner
        #Check for existing path

        if monster.path == None:
            monster_move_or_attack(monster)

        else:
            monster_move_or_attack(monster)


class ConfusedMonster:
    #AI for a temporarily confused monster, reverts to normal AI after a while
    def __init__(self, old_ai, num_turns=CONFUSE_NUM_TURNS):
        self.old_ai = old_ai
        self.num_turns = num_turns


    def take_turn(self):
        if self.num_turns > 0:  #still confused...
            #move in a random direction, and decrease the number of turns confused
            self.owner.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
            self.num_turns -= 1
        else:  #restore the previous AI (this one will be deleted because it's not referenced anymore)
            self.owner.ai = self.old_ai
            message('The ' + self.owner.name + ' is no longer confused!', libtcod.red)


class Item:
    #An item that can be picked up and used
    def __init__(self, use_function=None, pick_up_function=None, food_value=None):
        self.use_function = use_function
        self.pick_up_function = pick_up_function
        self.food_value = food_value


    def use(self):
        #special case: if the object has the Equipment component, the "use" action is to equip/dequip
        if self.owner.equipment:
            self.owner.equipment.toggle_equip()
            return
        elif self.food_value != None:
            player.fighter.player_eat_food(self)
        #just call the "use function" if it is defined
        elif self.use_function is None:
            message('The ' + self.owner.name + ' cannot be used.')
        else:
            if self.use_function() != 'cancelled':
                inventory.remove(self.owner)  #destroy after use, unless it was cancelled for some reason


    def pick_up(self):

        if self.pick_up_function != None:
            #the object has a pickup function, so use it and break the loop
            self.pick_up_function()

        #add to the player's inventory and remove from the map
        if len(inventory) >= 26:
            message('Your inventory is too full, cannot pick up ' + self.owner.name + '.', libtcod.yellow)
        else:
            inventory.append(self.owner)
            objects.remove(self.owner)
            message('You picked up a ' + self.owner.name + '!', libtcod.green)

            #special case: automatically equip if the corresponding equipment slot is unused
            equipment = self.owner.equipment
            if equipment and get_equipped_in_slot(equipment.slot) is None:
                equipment.equip()

    def drop(self):
        #add to the map and remove from the player's inventory. Also, place it at the players coordinates
        objects.append(self.owner)
        inventory.remove(self.owner)
        self.owner.x = player.x
        self.owner.y = player.y
        message('You dropped a ' + self.owner.name + '.', libtcod.yellow)

        #special case: if the object has the Equipment component, dequip it before dropping
        if self.owner.equipment:
            self.owner.equipment.dequip()


class Equipment:
    #an object that can be equipped, yielding bonuses. Automatically adds the Item component
    def __init__(self, slot, power_bonus_dice=0, power_bonus_sides=0, defense_bonus_dice=0, defense_bonus_sides=0, evasion_bonus_dice=0, evasion_bonus_sides=0, accuracy_bonus_dice=0, accuracy_bonus_sides=0, max_hp_bonus=0):
        self.power_bonus_dice = power_bonus_dice
        self.power_bonus_sides = power_bonus_sides
        self.defense_bonus_dice = defense_bonus_dice
        self.defense_bonus_sides = defense_bonus_sides
        self.evasion_bonus_dice = evasion_bonus_dice
        self.evasion_bonus_sides = evasion_bonus_sides
        self.accuracy_bonus_dice = accuracy_bonus_dice
        self.accuracy_bonus_sides = accuracy_bonus_sides
        self.max_hp_bonus = max_hp_bonus

        self.slot = slot
        self.is_equipped = False

    def toggle_equip(self):  #toggle equip/dequip status
        if self.is_equipped:
            self.dequip()
        else:
            self.equip()

    def equip(self):
        #if the slot is already being used, dequip whatever is there first
        old_equipment = get_equipped_in_slot(self.slot)
        if old_equipment is not None:
            old_equipment.dequip()

        #equip object and show a message about it
        self.is_equipped = True
        message('Equipped ' + self.owner.name + ' on ' + self.slot + '.', libtcod.light_green)

    def dequip(self):
        #dequip object and show a message about it
        if not self.is_equipped: return
        self.is_equipped = False
        message('Dequipped ' + self.owner.name + ' from ' + self.slot + '.', libtcod.light_yellow)


class Effect:
    #an effect that can be applied to the character, yielding bonuses or nerfs
    def __init__(self, effect_name=None, duration=0, turns_passed=0, base_duration=0, power_effect_dice=0, power_effect_sides=0, defense_effect_dice=0, defense_effect_sides=0, evasion_effect_dice=0, evasion_effect_sides=0, accuracy_effect_dice=0, accuracy_effect_sides=-0,
                 max_hp_effect=0, applied_times=1, confused=False, burning=False, damage_by_turn=None, paralyzed=None,
                 fatal_alert=False, mutation=False, m_loop=0, m_loop_turn=0, m_elec=False, m_elec_count=0,
                 m_elec_trigger=5, m_elec_damage=0):
        self.effect_name = effect_name
        self.duration = duration
        self.turns_passed = turns_passed
        self.base_duration = base_duration
        self.power_effect_dice = power_effect_dice
        self.power_effect_sides = power_effect_sides
        self.defense_effect_dice = defense_effect_dice
        self.defense_effect_sides = defense_effect_sides
        self.evasion_effect_dice = evasion_effect_dice
        self.evasion_effect_sides = evasion_effect_sides
        self.accuracy_effect_dice = accuracy_effect_dice
        self.accuracy_effect_sides = accuracy_effect_sides
        self.max_hp_effect = max_hp_effect
        self.applied_times = applied_times
        self.confused = confused
        self.burning = burning
        self.damage_by_turn = damage_by_turn
        self.paralyzed = paralyzed
        self.fatal_alert = fatal_alert
        self.is_active = False
        self.mutation = mutation

        self.m_loop = m_loop
        self.m_loop_turn = m_loop_turn
        self.m_elec = m_elec
        self.m_elec_count = m_elec_count
        self.m_elec_trigger = m_elec_trigger
        self.m_elec_damage = m_elec_damage


def monster_move_or_attack(monster):
    #If the monster is in the players FOV, monster can see player.
    if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):  #If the monster is in the players FOV

        # pygmys can attack one block further in every direction.
        #if monster.char == 'p' and monster.distance_to(player) <= 2:
            #if player.fighter.hp > 0:
                #monster.fighter.attack(player)

        #move towards player if far away
        if monster.distance_to(player) >= 2:
            #compute how to reach the player

            #Set old map tile to pathable
            libtcod.map_set_properties(fov_map, monster.x, monster.y, True, True)

            #Move monster
            monster.move_towards(player.x, player.y)

            #Set new map tile to not pathable
            libtcod.map_set_properties(fov_map, monster.x, monster.y, True, False)

            check_run_effects(monster)

        #close enough, attack! (if the player is still alive.)
        elif player.fighter.hp > 0:
            monster.fighter.attack(player)

            check_run_effects(monster)



    #TODO: Insert following line and find a way to path to the last free tile in path
    elif libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
        #Path to nearest monster
        for obj in objects:
            if obj.fighter and obj != monster and obj != player:
                #Set old map tile to pathable
                libtcod.map_set_properties(fov_map, monster.x, monster.y, True, True)

                #Move monster
                monster.move_towards(obj.x, obj.y)

                #Set new map tile to not pathable
                libtcod.map_set_properties(fov_map, monster.x, monster.y, True, False)

    else:
        #the player cannot see the monster
        #if we have an old path, follow it

        #If path is not empty and the distance to the player is greater than 2
        if monster.path != None and monster.path is not libtcod.path_is_empty(monster.path):


            nextx, nexty = libtcod.path_walk(monster.path, False)

            if nextx or nexty is not None:
                dx = nextx - monster.x
                dy = nexty - monster.y
                #Set old map tile to pathable
                libtcod.map_set_properties(fov_map, monster.x, monster.y, True, True)

                monster.move(dx, dy)

                #Set new map tile to not pathable
                libtcod.map_set_properties(fov_map, monster.x, monster.y, True, False)

            else:
                print 'no nextx or next line 770'

        #stop boar and baby boars and pygmys from wandering
        elif not monster.char == 'B' or monster.char == 'b' or monster.char == 'p':
            #path is empty, wander randomly
            rand_direction = libtcod.random_get_int(0, 1, 12)
            if rand_direction == 1:
                monster.move(-1, 1)
            elif rand_direction == 2:
                monster.move(0, 1)
            elif rand_direction == 3:
                monster.move(1, 1)
            elif rand_direction == 4:
                monster.move(-1, 0)
            elif rand_direction == 5:
                monster.move(1, 0)
            elif rand_direction == 6:
                monster.move(-1, -1)
            elif rand_direction == 7:
                monster.move(0, -1)
            elif rand_direction == 8:
                monster.move(1, -1)
            else:
                #Don't wander
                monster.move(0, 0)
        else:
            return 'cancelled'


def roll(dice, sides):
    result = 0
    for i in range(0, dice, 1):
        roll = libtcod.random_get_int(0, 1, sides)
        result += roll


def check_run_effects(obj):
    global fov_recompute

    # Check for effects, if there is 1 or more and their turns_passed value is not == duration, increase its turn_passed value by one, if it is equal to duration remove it.
    if obj.fighter.effects is not None:
        for eff in obj.fighter.effects:

            #Deal with non mutation effects
            if eff.mutation == False:

                # If it is the first time
                if eff.turns_passed == 0:
                    is_active = True


                #Run for damage_by_turn value in effects class, if there is a value, damage the obj by that value:
                if eff.damage_by_turn is not None:
                    obj.fighter.take_damage(eff.damage_by_turn)

                # check for fatal turn_by_damage limit if effect has damage_by_turn
                if eff.damage_by_turn is not None:

                    turns_left = eff.duration - eff.turns_passed

                    total_dmg = turns_left * eff.damage_by_turn

                    #If total damage to be dealt is larger than the players hp and the players hp is 1 or more
                    if total_dmg >= obj.fighter.hp and obj.fighter.hp >= 1:
                        #Todo make this a class variable in fighter.
                        FATAL_EFFECT = True
                        FATAL_NAME = str(eff.effect_name)
                        eff.fatal_alert = True
                        message('You are fatally ' + eff.effect_name + '!')
                        #works up to here, then doesn't want to print the warning
                        libtcod.console_print_ex(panel, 1, 4, libtcod.BKGND_NONE, libtcod.LEFT,
                                                 'Fatally ' + FATAL_NAME + '!')
                    elif eff.fatal_alert == True and player.fighter.hp >= 1:
                        FATAL_EFFECT = False
                        FATAL_NAME = None
                        message('You are no longer fatally ' + eff.effect_name + '.')
                        eff.fatal_alert = False

                #If the effect causes paralysis, set fighter paralysis to true
                if eff.paralyzed != None:
                    obj.fighter.paralysis = True

                #if turns_passed is equal to duration, remove the effect
                if eff.turns_passed == eff.duration:
                    #if the effect caused paralysis, set the fighters variable to False to allow movement again
                    if eff.paralyzed != None:
                        obj.fighter.paralysis = False
                        message('You can move again!')
                    obj.fighter.remove_effect(eff)
                    eff.turns_passed = 0

                #If turns_passed is not equal to the duration, add one turn
                if eff.turns_passed < eff.duration:
                    eff.turns_passed += 1

            #If it is a mutation
            elif eff.mutation == True:
                if eff.m_elec == True:
                    #Each application halves the turns needed to charge
                    real_trigger = eff.m_elec_trigger / eff.applied_times
                    if eff.m_elec_count < real_trigger:
                        eff.m_elec_count += 1
                    #if it has accumulated enough turns
                    if eff.m_elec_count >= real_trigger:
                        for obj in objects:
                            fire_times = eff.applied_times
                            fired_times = 0

                            #Find an object that isn't the player within 1 tile and fire if fired_times < fire_times
                            if obj.fighter and player.distance_to(
                                    obj) <= 1 and obj != player and obj.fighter.hp > 1 and fired_times < eff.applied_times:
                                #Tell render_all() to run elec flash routine
                                map[obj.x][obj.y].color_flash = libtcod.light_blue

                                message('You feel a tingle.. Press space to continue', libtcod.white)
                                render_all()  #may be unnecessary
                                #Update msgs
                                update_msgs()
                                #And wait for space key to cotinue
                                wait_for_spacekey()

                                message('A bolt of lightning hits the ' + str(obj.name) + ' for ' + str(
                                    eff.m_elec_damage) + ' damage!', libtcod.white)

                                obj.fighter.take_damage(eff.m_elec_damage)
                                eff.m_elec_count = 0
                                fired_times += 1

                                #Set map.diff_color to darkest_grey. This order is important.
                                map[obj.x][obj.y].diff_color = libtcod.darker_grey



                            #Function has completed, reset fired_times
                            if fired_times == fire_times:
                                fired_times = 0
    else:
        return 'no effects'


def number_of_turns():
    global turn_increment, turn_5
    turns = turn_increment + (turn_5 * 5)
    return turns


def update_msgs():
    #prepare to render the msgs panel
    libtcod.console_set_default_background(msgs, BORDER_BACKGROUND)
    libtcod.console_clear(msgs)
    #Color borders
    libtcod.console_set_default_foreground(msgs, BORDER_COLOR)

    for y_num in range(1, MSG_HEIGHT, 1):
        ##MSGS HOZ VERTICAL BORDERS##
        #Do the left side for messages
        libtcod.console_put_char(msgs, 0, y_num, BORDER_FILL, libtcod.BKGND_SCREEN)

        #Do the right side for messages
        libtcod.console_put_char(msgs, MSG_STOP - 1, y_num, BORDER_FILL, libtcod.BKGND_SCREEN)

        #Set border for msgs
    border = calc_border(MSG_STOP)

    #Top and bottom border bar for msgs
    #Top
    libtcod.console_print_ex(msgs, 0, 0, libtcod.BKGND_SCREEN, libtcod.LEFT, border)
    #Bottom
    libtcod.console_print_ex(msgs, 0, MSG_HEIGHT, libtcod.BKGND_SCREEN, libtcod.LEFT, border)

    y = 1
    for (line, color) in game_msgs:
        libtcod.console_set_default_foreground(msgs, color)
        libtcod.console_print_ex(msgs, 1, y, libtcod.BKGND_NONE, libtcod.LEFT, line)

        y += 1

    libtcod.console_blit(msgs, 0, 0, MSG_STOP, 0, 0, MSG_X, PANEL_Y)

def roll_for(list):

    roll_total = 0
    #For i in range of the list's first value (which should be the number of dice)
    for i in range(0, list[0], 1):
        #Roll for a number between 1 and the second value (which should be the sides)
        roll_total += libtcod.random_get_int(0, 1, list[1])

    return roll_total


def count_turns(turn_duration):  #Returns a true value when no_of_turns has passed
    global turn_increment, turn_5
    turn_start_number = number_of_turns()
    while not turn_duration == (turn_start_number - number_of_turns()):
        return False
    if turn_duration == (turn_start_number - number_of_turns()):
        return True


def create_room(room):
    global map
    # go through the tiles in the rectangle and make them passable
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            map[x][y].blocked = False
            map[x][y].block_sight = False



def place_objects(room):
    #maximum number of monsters per room
    max_monsters = from_dungeon_level([[2, 1], [3, 4], [5, 6]])

    #TODO: Min_monsters to create minimum danger level.


    #chance of each monsters
    monster_chances = {}
    monster_chances['Dog'] = 30  #Dog always spawns, even if all other monsters have 0 chance
    monster_chances['Snake'] = from_dungeon_level([[3, 1], [5, 3], [50, 7]])
    monster_chances['Imp'] = from_dungeon_level([[50, 2], [30, 5], [50, 7]])
    monster_chances['Firefly'] = from_dungeon_level([[3, 1], [30, 3], [60, 7]])
    monster_chances['Crab'] = from_dungeon_level([[1, 2], [30, 3], [60, 7]])
    monster_chances['Goat'] = from_dungeon_level([[15, 2], [30, 8], [60, 10]])
    monster_chances['Eagle'] = from_dungeon_level([[15, 5], [30, 8], [60, 10]])
    monster_chances['Pygmy'] = from_dungeon_level([[10, 5], [40, 8], [50, 10]])
    monster_chances['Bull'] = from_dungeon_level([[10, 6], [40, 7], [10, 9]])
    monster_chances['Centaur'] = from_dungeon_level([[5, 6], [20, 7], [30, 9]])

    #maximum number of items per room
    max_items = from_dungeon_level([[3, 1], [6, 4], [8, 6]])

    #minimum number of item attempts per room
    min_items = from_dungeon_level([[1, 1], [2, 4], [3, 6]])

    #choose random number of monsters
    num_monsters = libtcod.random_get_int(0, 0, max_monsters)

    #center coordinates of new room for placing bosses
    (new_x, new_y) = room.center()

    for i in range(num_monsters):
        #choose random spot for this monster
        x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
        y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

        #only place it if a tile is not blocked
        if not is_blocked(x, y):
            choice = random_choice(monster_chances)
            if choice == 'Dog':
                #create an dog
                fighter_component = Fighter(hp=10, defense_dice=1, defense_sides=5, power_dice=1, power_sides=8, evasion_dice=1, evasion_sides=4, accuracy_dice=2, accuracy_sides=4, xp=40, speed=10,
                                            death_function=monster_death)
                ai_component = BasicMonsterAI()
                monster = Object(x, y, 'd', 'Dog', libtcod.orange, blocks=True, fighter=fighter_component,
                                 ai=ai_component, description='A large, brown muscular looking dog. His eyes glow red.')

            elif choice == 'Snake':
                #create a Snake
                effect_component = Effect('poisoned', duration=5, damage_by_turn=2, base_duration=5)
                effect_roll = 20
                fighter_component = Fighter(hp=8, defense_dice=1, defense_sides=3, power_sides=5, power_dice=1, xp=100, speed=10, evasion_dice=1, evasion_sides=3, accuracy_dice=2, accuracy_sides=2, cast_effect=effect_component, cast_roll=effect_roll, death_function=monster_death)
                ai_component = BasicMonsterAI()
                monster = Object(x, y, 's', 'Snake', libtcod.lime, blocks=True, fighter=fighter_component,
                                 ai=ai_component,
                                 description='A light green snake covered in thousands of small, glistening scales, it looks poisonous.')

            elif choice == 'Imp':
                #create an Imp
                fighter_component = Fighter(hp=5, defense=10, power=7, xp=50, ev=8, acc=9, speed=9,
                                            death_function=monster_death)
                ai_component = BasicMonsterAI()
                monster = Object(x, y, 'i', 'Imp', libtcod.darker_green, blocks=True, fighter=fighter_component,
                                 ai=ai_component, description='A green Imp, skilled in defensive fighting.')

            elif choice == 'Eagle':
                #create an eagle
                fighter_component = Fighter(hp=100, defense=3, power=10, xp=200, ev=20, acc=10, speed=10,
                                            death_function=monster_death)
                ai_component = BasicMonsterAI()
                monster = Object(x, y, 'e', 'Eagle', libtcod.darker_sepia, blocks=True, fighter=fighter_component,
                                 ai=ai_component,
                                 description='A huge brown eagle, his muscular wings and razor sharp beak look threatening.')

            elif choice == 'Firefly':
                #create a glow fly
                effect_component = Effect('Paralyzed', duration=5, paralyzed=True, base_duration=5)
                effect_roll = 5
                fighter_component = Fighter(hp=8, defense_dice=1, defense_sides=3, power_dice=3, power_sides=3, xp=100, speed=9, evasion_dice=1, evasion_sides=3, accuracy_dice=2, accuracy_sides=2, cast_effect=effect_component, cast_roll=effect_roll, death_function=monster_death)
                ai_component = BasicMonsterAI()
                monster = Object(x, y, 'f', 'Firefly', libtcod.light_green, blocks=True, fighter=fighter_component,
                                 ai=ai_component,
                                 description='A small paralytic firefly. He moves very fast, but looks weak.')

            elif choice == 'Pygmy':
                #create a pygmy
                fighter_component = Fighter(hp=120, defense=6, power=8, xp=250, ev=20, acc=10, speed=10,
                                            death_function=monster_death)
                ai_component = BasicMonsterAI()
                monster = Object(x, y, 'p', 'Chieftain', libtcod.darkest_pink, blocks=True, fighter=fighter_component,
                                 ai=ai_component,
                                 description='A Pygmy chieftan, a particularly strong Pygmy who guides the others in matters of warfare. He looks much stronger than the others.')
                #Generate random number of pygmys
                num_pygmys = libtcod.random_get_int(0, 1, 6)
                for i in range(num_pygmys):
                    #choose random spot for baby boars
                    x = libtcod.random_get_int(0, monster.x + 2, monster.x - 2)
                    y = libtcod.random_get_int(0, monster.y + 2, monster.y - 2)
                    if not is_blocked(x, y):
                        #create other pygmys
                        fighter_component = Fighter(hp=100, defense=4, power=4, xp=200, ev=20, acc=10, speed=10,
                                                    death_function=monster_death)
                        ai_component = BasicMonsterAI()
                        other_pygmy = Object(x, y, 'p', 'Pygmy', libtcod.dark_pink, blocks=True,
                                             fighter=fighter_component, ai=ai_component,
                                             description='A member of an ancient tribe of warrior midgets, they rarely hunt alone. They carry long spears. His chieftan is sure to be nearby.')
                        #append the little fuckers
                        objects.append(other_pygmy)

            elif choice == 'Goat':
                #create a goat
                fighter_component = Fighter(hp=140, defense=4, power=5, xp=60, ev=25, acc=10, speed=8,
                                            death_function=monster_death)
                ai_component = BasicMonsterAI()
                monster = Object(x, y, 'g', 'Goat', libtcod.lighter_grey, blocks=True, fighter=fighter_component,
                                 ai=ai_component,
                                 description='A goat, with gnarled grey hair and wispy beard. He looks fast.')

            elif choice == 'Bull':
                #create a bull
                fighter_component = Fighter(hp=200, defense=1, power=8, xp=250, ev=20, acc=10, speed=10,
                                            death_function=monster_death)
                ai_component = BasicMonsterAI()
                monster = Object(x, y, chr(142), 'Bull', libtcod.light_flame, blocks=True, fighter=fighter_component,
                                 ai=ai_component,
                                 description='An enormous bull with two shining horns, they appear as if they have been polished. Perhaps by the bulls long rough tongue. He is extremely muscular and fast.')

            elif choice == 'Crab':
                #create a crab
                fighter_component = Fighter(hp=50, defense=6, power=9, xp=50, ev=30, acc=10, speed=12,
                                            death_function=monster_death)
                ai_component = BasicMonsterAI()
                monster = Object(x, y, 'c', 'Crab', libtcod.dark_yellow, blocks=True, fighter=fighter_component,
                                 ai=ai_component,
                                 description='A very large yellow crab, he skitters slowly sideways across the floor using his armored legs. He looks tough but slow.')

            elif choice == 'Centaur':
                #create a centaur
                fighter_component = Fighter(hp=180, defense=7, power=10, xp=300, ev=20, acc=14, speed=9,
                                            death_function=monster_death)
                ai_component = BasicMonsterAI()
                monster = Object(x, y, 'C', 'Centaur', libtcod.darker_magenta, blocks=True, fighter=fighter_component,
                                 ai=ai_component,
                                 description='A mythical creature; half human, half horse. He has the speed of a beast, and the dexterity of a man.')

            objects.append(monster)


    #choose random number of items
    num_items = libtcod.random_get_int(0, 0, max_items)

    for i in range(num_items):
        #choose random spot for this item
        x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
        y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

        # Set weaponchances functions and variables to work
        # How to do this in modules?
        weaponchances.dungeon_level = dungeon_level
        weaponchances.objects = objects
        weaponchances.Equipment = Equipment
        weaponchances.Object = Object
        weaponchances.Item = Item
        weaponchances.hunger_level = hunger_level
        weaponchances.cast_heal = cast_heal
        weaponchances.cast_lightning = cast_lightning
        weaponchances.cast_confuse = cast_confuse
        weaponchances.cast_fireball = cast_fireball
        weaponchances.message = message

        if not is_blocked(x, y):
            #only place it if the tile is not blocked

            weaponchances.create_item(x, y)

            # Roll new coordinates for food+scrolls
            x_roll = libtcod.random_get_int(0, -1, 1)
            y_roll = libtcod.random_get_int(0, -1, 1)
            x1 = x
            y1 = y
            x = x1 + x_roll
            y = y1 + y_roll

            if not is_blocked(x, y):
                weaponchances.add_food_and_scrolls(x, y)

            if not is_blocked(x, y):
                add_bones(x, y)




def place_special_rooms():  #TODO: Redo the dungeon generation to allow for special rooms, or ensure v_tun and h_tun will not intersect special room
    global map, objects, stairs, dungeon_level, rooms
    if dungeon_level == 1:
        #random width and height
        w = 6
        h = 18
        #random position without going out of the boundaries of the map
        x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
        y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)

        #"Rect" class makes rectangles easier to work with
        special_room = Rect(x, y, w, h)

        create_room(special_room)

        (new_x, new_y) = special_room.center()
        decx = new_x - 2
        decy = new_y + 10
        #place objects in room:
        for x in range(9):
            decy -= 2

            decoration = Object(decx, decy, chr(159), 'Fountain', libtcod.lighter_blue, blocks=True, decorative=True, always_visible=True)

            objects.append(decoration)
        decx = new_x + 2
        decy = new_y + 10
        for x in range(9):
            decy -= 2
            decoration = Object(decx, decy, chr(159), 'Fountain', libtcod.lighter_blue, blocks=True, decorative=True, always_visible=True)
            objects.append(decoration)


def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    #render a bar (HP, experience, etc.) first calculate the width of the bar
    bar_width = int(float(value) / maximum * total_width)

    #render the background first
    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    #now render the bar on top
    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    #finally, some centered text with the values
    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
                             name + ': ' + str(value) + '/' + str(maximum))


def render_bar_simple(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    #render a bar (HP, experience, etc.) first calculate the width of the bar
    bar_width = int(float(value) / maximum * total_width)

    #render the background first
    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    #now render the bar on top
    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    #finally, some centered text with the values
    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
                             name)

def return_description_under_mouse():
    global mouse

    #return a string with the names of all objects under the mouse
    (x, y) = (mouse.cx, mouse.cy)

    #create a list with the names of all objects at the mouse's coordinates and in FOV
    name_description = []
    for obj in objects:
        if obj.x == x and obj.y == y and libtcod.map_is_in_fov(fov_map, obj.x, obj.y):
            name_description.append(str(obj.name)+':\n')
            name_description.append(str(obj.description))

    result = ' '.join(name_description)

    return result


def get_names_under_mouse():
    global mouse

    #return a string with the names of all objects under the mouse
    (x, y) = (mouse.cx, mouse.cy)

    #create a list with the names of all objects at the mouse's coordinates and in FOV
    names = [obj.name for obj in objects if obj.x == x and obj.y == y and libtcod.map_is_in_fov(fov_map, obj.x, obj.y)]

    names = ', '.join(names)  #join the names, seperated by commas
    return names.capitalize()


def description_menu(header):
    global mouse

    #return a string with the names of all objects under the mouse
    (x, y) = (mouse.cx, mouse.cy)

    #create a list with the names of all objects at the mouse's coordinates and in FOV
    names = [obj for obj in objects if
             obj.x == x and obj.y == y and libtcod.map_is_in_fov(fov_map, obj.x, obj.y) and obj.description is not None]

    #show a menu with each object under the mouse as an option
    if len(names) == 0:
        options = ['There is nothing here.']
    else:
        options = [object.name for object in names]

    index = menu(header, options, INVENTORY_WIDTH)

    #if an item was chosen, return it
    if index is None or len(names) == 0: return None
    object = names[index]
    return object


def is_blocked(x, y):
    #first test the map tile
    if map[x][y].blocked:
        return True

    #now check for any blocking objects
    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            return True

    return False


def create_h_tunnel(x1, x2, y):
    global map
    #horizontal tunnel. min() and max() are used in case x1>x2
    for x in range(min(x1, x2), max(x1, x2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False


def create_v_tunnel(y1, y2, x):
    global map
    #vertical tunnel
    for y in range(min(y1, y2), max(y1, y2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False


def make_map():
    global map, objects, stairs, dungeon_level, rooms
    #the list of objects with just the player
    objects = [player]
    #fill map with "blocked" tiles
    map = [[Tile(True)
            for y in range(MAP_HEIGHT)]
           for x in range(MAP_WIDTH)]

    rooms = []

    num_rooms = 0

    place_special_rooms()

    for r in range(MAX_ROOMS):
        #random width and height
        w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        #random position without going out of the boundaries of the map
        x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 2)
        y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 2)

        #"Rect" class makes rectangles easier to work with
        new_room = Rect(x, y, w, h)

        #run through the other rooms and see if they intersect
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break

        if not failed:
            #this means there are no intersections, so this room is valid

            #"paint" it to the map's tiles
            create_room(new_room)

            #add some contents to this room, such as monsters as long as it is not the first room
            if num_rooms != 0:
                place_objects(new_room)

            #center coordinates of new room, will be useful later
            (new_x, new_y) = new_room.center()

            if num_rooms == 0:
                #this is the first room, where the player starts at
                player.x = new_x
                player.y = new_y
            else:
                #all rooms after the first:
                #connect it to the previous room with a tunnel

                #center coordinates of previous room
                (prev_x, prev_y) = rooms[num_rooms - 1].center()

                #draw a coin (random number that is either 0 or 1)
                if libtcod.random_get_int(0, 0, 1) == 1:
                    #first move horizontally, then vertically
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)
                else:
                    #first move vertically, then horizontally
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)

            #finally, append the new room to the list
            rooms.append(new_room)

            # TODO: Get this to work, currently calls it's pick_up_function like eat_food does, have to
            # Press 'y' over and over after starting a new game as It appears to hang.

            #roll_lever = libtcod.random_get_int(0, 0, 1)
            #if roll_lever == 1:
            #create_inscribed_lever(new_x-1, new_y+1)

            num_rooms += 1

    #create stairs at the center of the last room
    stairs = Object(new_x, new_y, '>', 'stairs', libtcod.white, always_visible=True)
    objects.append(stairs)
    stairs.send_to_back()  # so it's drawn below the monsters

    #Roll for boss and create if roll >= 7
    roll = libtcod.random_get_int(0, 0, 10)
    if roll >= 6 and dungeon_level == 2:
        boar_mother(new_x, new_y)


def boar_mother(x, y):
    global map, rooms
    fighter_component = Fighter(hp=35, defense=2, power=7, xp=400, ev=20, acc=10, speed=10,
                                death_function=monster_death)
    ai_component = BasicMonsterAI()
    boar = Object(x, y, 'B', 'Giant Boar Mother', libtcod.darker_red, blocks=True, fighter=fighter_component,
                  ai=ai_component, description='A big angry ')
    #Generate random number of baby boars
    num_babies = libtcod.random_get_int(0, 15, 35)
    #append boar before it is used to generate babies
    objects.append(boar)
    for i in range(num_babies):
        #choose random spot for baby boars
        x = libtcod.random_get_int(0, boar.x + 2, boar.x - 2)
        y = libtcod.random_get_int(0, boar.y + 2, boar.y - 2)
        if not is_blocked(x, y):
            #create baby boars
            fighter_component = Fighter(hp=2, defense=0, power=3, xp=5, ev=1, acc=10, speed=10,
                                        death_function=monster_death)
            ai_component = BasicMonsterAI()
            monster = Object(x, y, 'b', 'Baby boar', libtcod.darkest_red, blocks=True, fighter=fighter_component,
                             ai=ai_component, description='A baby boar, how cute.')
            #append the little fuckers
            objects.append(monster)


def menu(header, options, width):
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

    #calculate the total height for the header (afer auto wrap) and one line per option
    header_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
    if header == '':
        header_height = 0
    height = len(options) + header_height

    #create an off-screen console that represents the menu's window
    window = libtcod.console_new(width, height)

    #print the header, with auto wrap, baby.
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    #print all the options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1

    #blit the contents of "window" to the root console
    x = SCREEN_WIDTH / 2 - width / 2
    y = SCREEN_HEIGHT / 2 - height / 2
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    #present the root console to the player and wait for keypress
    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)

    if key.vk == libtcod.KEY_ENTER and key.lalt:  #(special case) Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    #convert the ASCII code to an index; if it corresponds to an option, return it
    index = key.c - ord('a')
    if index >= 0 and index < len(options): return index
    return None


def inventory_menu(
        header):  #TODO: Find a way to sit all copies of an item into a single option and present it, adjusting the value of the option by -1 if chosen
    #show a menu with each item of the inventory as an option
    if len(inventory) == 0:
        options = ['Inventory is empty.']
    else:
        options = []
        for item in inventory:
            text = item.name
            #show additional information, in case it's equipped
            if item.equipment and item.equipment.is_equipped:
                text = text + ' (on ' + item.equipment.slot + ')'
            options.append(text)

    index = menu(header, options, INVENTORY_WIDTH)

    #if an item was chosen, return it
    if index is None or len(inventory) == 0: return None
    return inventory[index].item

def msgbox(text, width=50):
    menu(text, [], width)  #use menu() as a sort of "message box"


def render_all():
    global fov_map, color_dark_wall, color_light_wall
    global color_dark_ground, color_light_ground
    global fov_recompute
    global objects
    global turn
    global hunger_level
    global FOV_TORCHX, noise, FOV_PX, FOV_PY, FOV_NOISE, NOISE

    if fov_recompute:
        libtcod.console_clear(con)
        #recompute FOV if needed (the player moved or something)
        fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

        #go through all tiles and set their background color
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                wall = map[x][y].block_sight

                #If the tile has not yet had its color_set value set, set it using perlin noise.
                if map[x][y].color_set == None:

                    if wall == True:
                        base = color_set_wall_dark
                        light = color_dark_wall
                        base_char = color_char_set_dark_wall
                        light_char = color_char_dark_wall

                    elif wall == False:
                        base = color_dark_ground
                        light = color_set_ground_dark
                        base_char = color_char_set_dark_ground
                        light_char = color_char_dark_ground

                    l = libtcod.random_get_float(0, 0, 1.0)

                    light = libtcod.color_lerp(base, light, l)
                    light_char = libtcod.color_lerp(base_char, light_char, l)

                    map[x][y].color_set = light
                    map[x][y].color_fore = light_char


                if not visible:
                    #if it's not explored right now, the player can only see it if it's explored
                    if map[x][y].explored:
                        if wall:
                            #Use lerped and stored variable for this tiles background color
                            libtcod.console_set_char_background(con, x, y, map[x][y].color_set, libtcod.BKGND_SET)
                            #Use lerped and stored variable for this tiles foreground color
                            libtcod.console_set_default_foreground(con, map[x][y].color_fore)
                            #Set character
                            libtcod.console_put_char(con, x, y, WALL_CHAR, libtcod.BKGND_SCREEN)
                        else:
                            #Use lerped and stored variable for this tiles background color
                            libtcod.console_set_char_background(con, x, y, map[x][y].color_set, libtcod.BKGND_SET)
                            #Use lerped and stored variable for this tiles foreground color
                            libtcod.console_set_default_foreground(con, map[x][y].color_fore)
                            #Set character
                            libtcod.console_put_char(con, x, y, FLOOR_CHAR, libtcod.BKGND_SCREEN)
                else:

                    #it's visible
                    if wall:

                        #Use lerped and stored variable for this tiles foreground color
                        libtcod.console_set_default_foreground(con, map[x][y].color_fore)
                        libtcod.console_put_char(con, x, y, WALL_CHAR, libtcod.BKGND_SCREEN)

                        #Set base and light for torch noise lerp at end
                        base = color_dark_wall
                        light = color_light_wall
                        base_char = color_char_set_dark_wall
                        light_char = color_char_dark_wall

                    #Is ground, if map.diff_color is not None, render the color instead
                    elif map[x][y].diff_color is not None:
                        libtcod.console_set_char_background(con, x, y, map[x][y].diff_color, libtcod.BKGND_SET)

                        #If flash is true, render it once, then set to false, this shouldn't work as wait_for_spacekey()
                        #uses render_all() in its while loop. Problem lies elsewhere I think.
                    elif map[x][y].color_flash is not None:

                        #Make the color blue flash for one render
                        libtcod.console_set_char_background(con, x, y, map[x][y].color_flash, libtcod.BKGND_SET)

                        #Immediately set to false to ensure this only runs once
                        map[x][y].color_flash = None


                    #Else it is floor and has no diff_color value and should be set to the default color
                    else:

                        libtcod.console_set_default_foreground(con, libtcod.gold)
                        libtcod.console_put_char(con, x, y, FLOOR_CHAR, libtcod.BKGND_SCREEN)
                        base = color_dark_ground
                        light = color_light_ground
                        base_char = color_char_set_dark_ground
                        light_char = color_char_dark_wall

                    #############
                    #TORCH NOISE#
                    #############

                    # slightly change the perlin noise parameter
                    FOV_TORCHX += 0.2

                    # randomize the light position between -1.5 and 1.5
                    tdx = [FOV_TORCHX + 20.0]
                    dx = libtcod.noise_get(NOISE, tdx, libtcod.NOISE_SIMPLEX) * 1.5
                    tdx[0] += 30.0
                    dy = libtcod.noise_get(NOISE, tdx, libtcod.NOISE_SIMPLEX) * 1.5
                    di = 0.005 * libtcod.noise_get(NOISE, [FOV_TORCHX], libtcod.NOISE_SIMPLEX)

                    # cell distance to torch (squared)
                    r = float(x - player.x + dx) * (x - player.x + dx) + (y - player.y + dy) * (y - player.y + dy)

                    #Used to use calculated variable r, now uses distance_from()
                    if player.distance_from(x, y) < SQUARED_TORCH_RADIUS:
                        #Needs to use r as for some reason distance_from doesn't work
                        l = (SQUARED_TORCH_RADIUS - r) / SQUARED_TORCH_RADIUS + di
                        if l < 0.0:
                            l = -0.0
                        elif l > 1.6:
                            l = 1.6

                        if map[x][y].diff_color is not None:
                            #TODO: Make torch light change have an alpha, to make coloring easier.
                            light = libtcod.color_lerp(map[x][y].diff_color, light, l)

                        if wall:
                            light = libtcod.color_lerp(map[x][y].color_set, color_light_wall, l)
                            light_char = libtcod.color_lerp(map[x][y].color_fore, color_char_light_wall, l)
                        else:
                            light = libtcod.color_lerp(map[x][y].color_set, color_light_ground, l)
                            light_char = libtcod.color_lerp(map[x][y].color_fore, color_char_light_ground, l)

                    #Lerp tile in FOV's background
                    libtcod.console_set_char_background(con, x, y, light, libtcod.BKGND_SET)
                    #Lerp tile in FOV foreground
                    libtcod.console_set_char_foreground(con, x, y, light_char)

                    #May improve flicker
                    NOISE = libtcod.noise_new(1, 1.0, 1.0)

                    #Since it's visible, set it to explored
                    map[x][y].explored = True

        #Supposed to cause flicker, but does nothing.
        FOV_NOISE = libtcod.noise_new(1, 1.0, 1.0)




    #draw all objects in list, except the player, want it to always appear on top, so we draw it later
    for object in objects:
        if object != player:
            object.draw()

    player.draw()

    #Special damage_draw range count
    for object in objects:
        display_damage(object)

    #blit the contents of "con" to root console and present it
    libtcod.console_blit(con, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, 0, 0)

    #prepare to render the GUI panel
    libtcod.console_set_default_background(panel, BORDER_BACKGROUND)
    libtcod.console_clear(panel)

    # prepare and color the msgs background
    libtcod.console_set_default_background(msgs, BORDER_BACKGROUND)
    libtcod.console_clear(msgs)

    #prepare to render the second GUI panel
    libtcod.console_set_default_background(panel2, BORDER_BACKGROUND)
    libtcod.console_clear(panel2)

    ###########
    ##BORDERS##
    ###########

    #Prepare to render the borders
    libtcod.console_set_default_foreground(msgs, BORDER_COLOR)
    libtcod.console_set_default_foreground(panel, BORDER_COLOR)
    libtcod.console_set_default_foreground(panel2, BORDER_COLOR)

    #First, the vertical borders
    #For the height of panel, minus one for the top bar that already displays it.
    for y_num in range(1, MSG_HEIGHT, 1):
        ##MSGS VERTICAL BORDERS##
        #Do the left side for messages
        libtcod.console_put_char(msgs, 0, y_num, BORDER_FILL, libtcod.BKGND_SCREEN)

        #Do the right side for messages
        libtcod.console_put_char(msgs, MSG_STOP - 1, y_num, BORDER_FILL, libtcod.BKGND_SCREEN)

        ##HEALTH/POIS BARS VERTICAL BORDERS##
        #Do the left side for health bars
        libtcod.console_put_char(panel, 0, y_num, BORDER_FILL, libtcod.BKGND_SCREEN)

        #Right side already done

    #Different range, same function.
    for y_num in range(1, MAP_HEIGHT, 1):
        ##PANEL2 VERTICAL BORDERS##
        #Do the left side for messages
        libtcod.console_put_char(panel2, 0, y_num, BORDER_FILL, libtcod.BKGND_SCREEN)


        #Do the right side for messages
        libtcod.console_put_char(panel2, PANEL2_WIDTH - 1, y_num, BORDER_FILL, libtcod.BKGND_SCREEN)

    #Set border for msgs
    border = calc_border(MSG_STOP)

    #Top and bottom border bar for msgs
    #Top
    libtcod.console_print_ex(msgs, 0, 0, libtcod.BKGND_SCREEN, libtcod.LEFT, border)
    #Bottom
    libtcod.console_print_ex(msgs, 0, MSG_HEIGHT, libtcod.BKGND_SCREEN, libtcod.LEFT, border)

    #Set border for panel
    border = calc_border(SCREEN_WIDTH)

    #Top and bottom border bar for panel (health bars)
    #Top
    libtcod.console_print_ex(panel, 0, 0, libtcod.BKGND_SCREEN, libtcod.LEFT, border)
    #Bottom
    libtcod.console_print_ex(panel, 0, MSG_HEIGHT, libtcod.BKGND_SCREEN, libtcod.LEFT, border)

    #Set border for panel2
    border = calc_border(PANEL2_WIDTH)

    #Top and bottom border bar for panel2
    #Top
    libtcod.console_print_ex(panel2, 0, 0, libtcod.BKGND_SCREEN, libtcod.LEFT, border)
    #Bottom
    libtcod.console_print_ex(panel2, 0, MAP_HEIGHT - 1, libtcod.BKGND_SCREEN, libtcod.LEFT, border)
    #Middle
    libtcod.console_print_ex(panel2, 0, 23, libtcod.BKGND_SCREEN, libtcod.LEFT, border)

    ###############
    ##END BORDERS##
    ###############

    #print the game messages, one line at a time
    y = 1
    for (line, color) in game_msgs:
        libtcod.console_set_default_foreground(msgs, color)
        libtcod.console_print_ex(msgs, 1, y, libtcod.BKGND_NONE, libtcod.LEFT, line)

        y += 1

    #show the player's stats
    level_up_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
    render_bar(panel, 1, 1, BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp, libtcod.red,
               libtcod.darker_crimson)
    render_bar(panel, 1, 2, BAR_WIDTH, 'XP', player.fighter.xp, level_up_xp, libtcod.light_blue,
               libtcod.darkest_blue)
    render_bar_simple(panel, 1, 3, BAR_WIDTH, str(hunger()), hunger_level, HUNGER_TOTAL, libtcod.orange,
                      libtcod.darker_orange)

    #Check for total number of effects for gui
    total_effects = 1

    for eff in player.fighter.effects:

        if eff.effect_name == 'poisoned':
            render_bar_simple(panel, 1, 3 + total_effects, BAR_WIDTH, 'Poisoned X ' + str(eff.applied_times),
                              (eff.duration - eff.turns_passed), eff.duration, libtcod.darker_green,
                              libtcod.darkest_green)
            total_effects += 1

        if eff.effect_name == 'Paralyzed':
            render_bar_simple(panel, 1, 3 + total_effects, BAR_WIDTH, 'Paralyzed X ' + str(eff.applied_times),
                              (eff.duration - eff.turns_passed), eff.duration, libtcod.purple,
                              libtcod.darker_purple)
            total_effects += 1

        if eff.effect_name == 'electric power':
            render_bar_simple(panel, 1, 3 + total_effects, BAR_WIDTH, 'Electrified Level ' + str(eff.applied_times),
                              eff.m_elec_count, eff.m_elec_trigger / eff.applied_times, libtcod.blue,
                              libtcod.darker_yellow)
            total_effects += 1


    #display names of objects under the mouse
    libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    libtcod.console_print_ex(panel, MSG_STOP+BAR_WIDTH+1, 1, libtcod.BKGND_NONE, libtcod.LEFT, return_description_under_mouse())

    #blit the contents of "panel" to the root console
    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)

    #blit the contents of "msgs" to the root console
    libtcod.console_blit(msgs, 0, 0, MSG_STOP, 0, 0, MSG_X, PANEL_Y)

    #Change color from border color for panel2
    libtcod.console_set_default_foreground(panel2, libtcod.white)

    # display a title
    libtcod.console_print_ex(panel2, 5, 1, libtcod.BKGND_NONE, libtcod.LEFT, 'Enemies in FOV:')

    #print the enemy fighters hp, and a bar below them, as long as the total width does not exceed 16
    y = 2

    for obj in objects:
        # if object is in fov and is a fighter and is not the player, and the list of objects is not too
        #  long, render a bar for that object
        if libtcod.map_is_in_fov(fov_map, obj.x, obj.y) and obj.fighter and obj.name != 'player' and y <= 14:
            render_bar(panel2, 2, y, BAR_WIDTH, str(obj.name.capitalize()), obj.fighter.hp, obj.fighter.max_hp,
                       libtcod.red, libtcod.darker_red)
            y += 2

    # Print char box
    libtcod.console_print_rect_ex(panel2, 1, 24, PANEL2_WIDTH, RECT_HEIGHT, libtcod.BKGND_NONE, libtcod.LEFT,
                                  'Character Information:\n')

    char_info = '\nLevel: ' + str(player.level) + '\nDungeon level: ' + str(dungeon_level) + '\nAttack: ' + str(
        player.fighter.power) + '\nDefense: ' + str(
        player.fighter.defense) + '\nEvasion: ' + str(player.fighter.evasion) + '\nAccuracy: ' + str(
        player.fighter.accuracy) + '\nTurns: ' + total_turns() + '\n\nEffects: ' + get_player_effects() + '\n\nEquipped Items:' + iterate_through_list(
        get_all_equipped(player))

    libtcod.console_print_ex(panel2, 1, 26, libtcod.BKGND_NONE, libtcod.LEFT, char_info)

    #blit the contents of "panel2" to the root console
    libtcod.console_blit(panel2, 0, 0, PANEL2_WIDTH, MAP_HEIGHT, 0, MAP_WIDTH, 0)


def display_damage(self):
    #If object has been given a damage value by take_damage()
    if self.display_dmg != None and self != player:

        #DAMAGE PRINT#

        #Keep a count of the number of characters
        count = 0
        #calculate the number of chars required to print the damage
        list1 = str(self.display_dmg)

        #For each char entry in list1, set a foreground colour, the character for that tile.
        #also increase count to reflect change
        for i in list1:
            libtcod.console_set_default_foreground(con, libtcod.white)

            libtcod.console_put_char(con, self.x + count, self.y, str(i), libtcod.BKGND_SCREEN)
            count += 1

    #If self is player and player took damage, display a char.
    if self == player and self.display_dmg != None:
        libtcod.console_set_default_foreground(con, libtcod.darker_red)
        libtcod.console_set_char_background(con, self.x, self.y, libtcod.silver, libtcod.BKGND_SET)
        libtcod.console_put_char(con, self.x, self.y, '*', libtcod.BKGND_SCREEN)


def wait_for_spacekey():  #Make cast heal message appear without having to press the same key twice
    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)
    choice = None
    while choice == None:  #keep asking until a choice is made

        if key.vk == libtcod.KEY_SPACE:
            choice = 'space'
            return 'cancelled'
            libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
            fov_recompute = True
            render_all()

        #check for keypress, render and flush the screen to present monster inside fov.
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
        fov_recompute = True

        render_all()


def message_yn(messagequestion, messagey, color1=libtcod.white, color2=libtcod.white):
    message(messagequestion, color1)
    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)

    choice = None

    while choice == None:  # keep asking until a choice is made
        key_char = chr(key.c)
        if key_char == 'y':
            choice = 'y'
            message(messagey, color2)
            return choice
        if key_char == 'n':
            choice = 'n'
            return choice


def cast_inscribed_lever():
    message_yn(
        'You see a lever made of gold in the floor, it is inscribed with thousands of glyphs you do not recognize, do you wish to pull it? (y=yes, else=no',
        'You pull the lever.\nYou hear a thunderous CRACK split the air in two.', libtcod.yellow, libtcod.green)
    # if player pulled lever
    if message_yn == 'y':
        #roll for outcome
        roll = libtcod.random_get_int(0, 0, 1)
        if roll == 0:  # Spawn 6 weapon/items
            for i in range(0, 5, 1):
                weaponchances.random_item()
                weaponchances.create_item(player.x, player.y)
        else:
            pass


def create_inscribed_lever(x, y):
    item_component = Item(pick_up_function=cast_inscribed_lever())
    lever = Object(x, y, chr(207), 'Inscribed lever', libtcod.gold, item=item_component, always_visible=True)
    # needs to cast on pick up, not use.
    objects.append(lever)


def message_wait(char, messagetext, color=libtcod.white):
    #display message once when char comes into FOV then set seen to true
    for object in objects:
        if object.char == char and libtcod.map_is_in_fov(fov_map, object.x, object.y) and object.seen == False:
            render_all()
            #use message function to present message
            message(messagetext, color)
            render_all()
            #set object to seen
            object.seen = True
            #wait for keypress
            key = libtcod.console_wait_for_keypress(True)

            choice = None

            while choice == None:  #keep asking until a choice is made
                if key.vk == libtcod.KEY_SPACE:
                    choice == 'space'
                    return 'cancelled'
                #check for keypress, render and flush the screen to present monster inside fov.
                libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
                render_all()

                libtcod.console_flush()


def message(new_msg, color=libtcod.white):
    #split the message if necessary, among multiple lines
    new_msg_lines = textwrap.wrap(new_msg, MSG_STOP - 1)

    for line in new_msg_lines:
        #if the buffer is full, remove the first line to make room for the new one
        if len(game_msgs) == MSG_HEIGHT - 1:
            del game_msgs[0]

        #add the new line as a tuple, with the text and the color
        game_msgs.append((line, color))


def player_move_or_attack(dx, dy):
    global fov_recompute

    outcome = None

    #If player is paralyzed, return string
    if player.fighter.paralysis == True:
        outcome = 'paralyzed'
        message('You are paralyzed and cannot move!', libtcod.white)


    #Else, move or attack
    elif player.fighter.paralysis == False:
        x = player.x + dx
        y = player.y + dy
        no_move = False
        if x == player.x and y == player.y:
            no_move = True

        target = None
        for obj in objects:
            if obj.fighter and obj.x == x and obj.y == y and obj != player:
                target = obj
                break

        if target != None:
            player.fighter.attack(target)
            outcome = 'moved'
            fov_recompute = True

        elif no_move is True:
            message('You rest a turn.', libtcod.white)
            outcome = 'moved'
            fov_recompute = True
            no_move = False

        elif is_blocked(x, y):
            message('You stumble into the wall..', libtcod.white)
            outcome = 'stumble'

        elif is_blocked(x, y) == False:
            player.move(dx, dy)
            fov_recompute = True
            outcome = 'moved'


    return outcome


def handle_keys():
    global keys;
    global hunger_level

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #Alt + Enter toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    elif key.vk == libtcod.KEY_ESCAPE:
        return 'exit'  #Exit game

    if game_state == 'playing':

        #Shift run keys:

        if key.vk == libtcod.KEY_UP and key.lalt or key.vk == libtcod.KEY_KP8  and key.lalt:
            shift_run(player, 0, -1)

        elif key.vk == libtcod.KEY_DOWN and key.lalt or key.vk == libtcod.KEY_KP2 and key.lalt:
            shift_run(player, 0, 1)

        elif key.vk == libtcod.KEY_LEFT and key.lalt or key.vk == libtcod.KEY_KP4 and key.lalt:
            shift_run(player, -1, 0)

        elif key.vk == libtcod.KEY_RIGHT and key.lalt or key.vk == libtcod.KEY_KP6 and key.lalt:
            shift_run(player, 1, 0)

        elif key.vk == libtcod.KEY_HOME and key.lalt or key.vk == libtcod.KEY_KP7 and key.lalt:
            shift_run(player, -1, -1)

        elif key.vk == libtcod.KEY_PAGEUP and key.lalt or key.vk == libtcod.KEY_KP9 and key.lalt:
            shift_run(player, 1, -1)

        elif key.vk == libtcod.KEY_END and key.lalt or key.vk == libtcod.KEY_KP1 and key.lalt:
            shift_run(player, -1, 1)

        elif key.vk == libtcod.KEY_PAGEDOWN and key.lalt or key.vk == libtcod.KEY_KP3 and key.lalt:
            shift_run(player, 1, 1)

        elif key.vk == libtcod.KEY_KP5 and key.lalt:
            player_rest()


        #movement keys
        if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
            outcome = player_move_or_attack(0, -1)
            return outcome
        elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
            outcome = player_move_or_attack(0, 1)
            return outcome
        elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
            outcome = player_move_or_attack(-1, 0)
            return outcome
        elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
            outcome = player_move_or_attack(1, 0)
            return outcome
        elif key.vk == libtcod.KEY_HOME or key.vk == libtcod.KEY_KP7:
            outcome = player_move_or_attack(-1, -1)
            return outcome
        elif key.vk == libtcod.KEY_PAGEUP or key.vk == libtcod.KEY_KP9:
            outcome = player_move_or_attack(1, -1)
            return outcome
        elif key.vk == libtcod.KEY_END or key.vk == libtcod.KEY_KP1:
            outcome = player_move_or_attack(-1, 1)
            return outcome
        elif key.vk == libtcod.KEY_PAGEDOWN or key.vk == libtcod.KEY_KP3:
            outcome = player_move_or_attack(1, 1)
            return outcome
        elif key.vk == libtcod.KEY_KP5:
            pass  #do nothing ie wait for the monster to come to you
            outcome = player_move_or_attack(0, 0)
            return outcome


        #if key.vk == libtcod.KEY_ENTER and key.lalt:

        else:
            #test for other keys
            key_char = chr(key.c)

            if key_char == 'g':
                #pick up an item
                for object in objects:  #look for an item in the players tile
                    if object.x == player.x and object.y == player.y and object.item and object.char != '%':
                        object.item.pick_up()
                        break

            if key_char == 'i':
                #show the inventory; if an item is selected, use it.
                #\n is a line break to keep a space between header and options
                chosen_item = inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')

                if chosen_item is not None:
                    chosen_item.use()

            #debug
            if key_char == '[':
                player.fighter.hp = player.fighter.max_hp

            #debug
            if key_char == ']':
                for y in range(MAP_HEIGHT):
                    for x in range(MAP_WIDTH):
                        map[x][y].explored = True

            # debug
            if key_char == '@':
                player.fighter.max_hp = 1000
                player.fighter.base_defense_sides = 1000
                player.fighter.base_power_sides = 1000

            #debug
            if key_char == '#':
                player.fighter.take_damage(10)

            if key_char == 'r':
                player_rest()

            if key_char == 'd':
                #show the inventory; if an item is selected, drop it.
                chosen_item = inventory_menu('Press the key next to an item to drop it, or any other to canel.\n')
                if chosen_item is not None:
                    chosen_item.drop()

            if mouse.rbutton_pressed:
                #show the description menu, if an item is selected, describe it.
                chosen_object = description_menu('Press the key next to an object to see its description.\n')

                if chosen_object is not None:
                    render_all()
                    msgbox(str(chosen_object.name.capitalize()) + ':' + '\n\n' + str(chosen_object.description) + '\n',
                           CHARACTER_SCREEN_WIDTH)

            if key_char == '>':
                #go down stairs, if the player is on them
                if stairs.x == player.x and stairs.y == player.y:
                    next_level()

            if key_char == 'c':
                level_up_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
                msgbox(
                    'Character Information\n\nLevel: ' + str(player.level) + '\nExperience: ' + str(player.fighter.xp) +
                    '\nExperience to level up: ' + str(level_up_xp) + '\n\nHP: ' + str(
                        player.fighter.max_hp) + '\nAttack: ' + str(
                        player.fighter.power) + '\nDefense: ' + str(player.fighter.defense) + '\nEvasion: ' + str(
                        player.fighter.ev) + '\nAccuracy: ' + str(
                        player.fighter.acc) + '\nEffects: ' + get_player_effects(), CHARACTER_SCREEN_WIDTH)

            return 'didnt-take-turn'


def player_rest():
    carry_on = True
    while carry_on == True:
        if player.fighter.hp <= player.fighter.max_hp:

            for obj in objects:
                if obj.fighter and libtcod.map_is_in_fov(fov_map, obj.x, obj.y) and obj.name != 'player':
                    carry_on = False
                    message('That ' + obj.name + ' is too close for you to rest!', libtcod.red)

        if hunger_level <= HUNGER_WARNING:
            carry_on = False
            message('You are too hungry to rest! Eat some food.', libtcod.red)

        if FATAL_EFFECT == True:
            carry_on = False
            message('You cannot rest while fatally ' + FATAL_NAME + '!')

        if player.fighter.hp == player.fighter.max_hp:
            carry_on = False
            message('You are already at full health', libtcod.white)
            break

        if carry_on == True:
            check_by_turn(player.fighter.speed)
            check_run_effects(player)

        if player.fighter.hp == (player.fighter.max_hp / 2) - 1:
            carry_on = False
            message('You rest to regain some of your health', libtcod.darkest_green)
            player.fighter.hp += 1

        if player.fighter.hp == (player.fighter.max_hp / 1.25) - 1:
            carry_on = False
            message('You rest to regain most of your health', libtcod.darker_green)
            player.fighter.hp += 1

        if player.fighter.hp == player.fighter.max_hp:
            carry_on = False
            message('You rest to regain all of your health', libtcod.green)


def get_player_effects():  # Get player effects and return them in pargraphed strings

    list_effects = []
    for e in player.fighter.effects:
        list_effects.append(str(e.effect_name))

    list1 = []
    for i in list_effects:
        list1.append('\n ' + str(i).capitalize())

    return ' '.join(list1)


def closest_monster(max_range):
    #find closest enemy, up to a maximum range, and in the players FOV
    closest_enemy = None
    closest_dist = max_range + 1  #start with slightly more than max range

    for object in objects:
        if object.fighter and not object == player and libtcod.map_is_in_fov(fov_map, object.x, object.y):
            #calculate distance between this object and the player
            dist = player.distance_to(object)
            if dist < closest_dist:  # it's closer so remember it
                closest_enemy = object
                closest_dist = dist
    return closest_enemy


def cast_heal():
    #heal the player
    if player.fighter.hp == player.fighter.max_hp:
        message('You are already at full health.', libtcod.red)
        return 'cancelled'
    else:
        message('Your wounds pulse with a magical energy, some bind and close entirely! Press SPACE to continue.',
                libtcod.light_violet)
        player.fighter.heal(HEAL_AMOUNT)
        render_all()
        wait_for_spacekey()


def cast_lightning():
    #find nearest enemy (inside a maximum range) and damage it
    monster = closest_monster(LIGHTNING_RANGE)
    if monster is None:  #no enemy found within maximum range
        message('No enemy is close enough to strike.', libtcod.red)
        return 'cancelled'

    #Zap it like it's hot!
    message(
        'A lightning bolt thunders from the scroll with a loud clap and strikes the ' + monster.name + ' for ' + str(
            LIGHTNING_DAMAGE) + ' hit points. Press SPACE to continue.', libtcod.light_blue)
    monster.fighter.take_damage(LIGHTNING_DAMAGE)
    render_all()
    wait_for_spacekey()


def cast_confuse():
    #ask the player for a target to confuse
    message('Left-click to target an enemy and confuse it, right-click to cancel.', libtcod.light_cyan)
    monster = target_monster(CONFUSE_RANGE)
    if monster is None: return 'cancelled'

    old_ai = monster.ai
    monster.ai = ConfusedMonster(old_ai)
    monster.ai.owner = monster  #tell the compnent who owns it
    message(
        'You hear Dionysus laugh maniacally, the ' + monster.name + ' is touched by the god and becomes confused! Press SPACE to continue.',
        libtcod.light_green)
    render_all()
    wait_for_spacekey()


def cast_fireball():  #FIGURE OUT HOW TO PAUSE AFTER THIS MESSAGE BEFORE DEALING DAMAGE
    #ask the player for a target tile to throw a fireball at
    message('Lef-click a target tile for the fireball, or right_click to cancel.', libtcod.light_cyan)
    (x, y) = target_tile()
    if x is None: return 'cancelled'
    message(
        'Hephaestus turns his crippled body to you from an unseen dimension, and the air surrounding you explodes in a violent fireball! Press SPACE to continue.',
        libtcod.orange)

    update_msgs()
    wait_for_spacekey()

    for obj in objects:  #damage every fighter in range, including the player
        if obj.distance(x, y) <= FIREBALL_RADIUS and obj.fighter and obj != player:
            message('The ' + obj.name + ' is completely immolated and takes ' + str(FIREBALL_DAMAGE) + ' damage.',
                    libtcod.white)
            map[obj.x][obj.y].color_flash = libtcod.orange

            obj.fighter.take_damage(FIREBALL_DAMAGE)


def player_death(player):
    #the game ended!
    global game_state
    message('You died! Zeus will live on to terrorize the world. Good job.', libtcod.red)
    game_state = 'dead'

    #for added effect, transform the player into a corpse!
    player.char = '%'
    player.color = libtcod.dark_red

    #xp_total = TOTAL_XP + player.fighter.xp

    #Append xp_total, a name and the date to a new savefile for highscores
    #list1 = (xp_total, player.name, current_date)
    #file = shelve.open('highscores', 'n')
    #file[''] = xp_total


def monster_death(monster):
    #transform it into a nasty corpse! it doesn't block, can't be attacked and doesn't move.

    #Set tile to not block paths
    libtcod.map_set_properties(fov_map, monster.x, monster.y, True, True)


    #Explode it if was killed by war hammer

    equipped = get_all_equipped(player)
    for i in equipped:
        if i.owner.char == chr(24):
            #blow strength

            message(
                'The ' + str(monster.name) + ' explodes under the ferocious blow of your ' + str(i.owner.name) + '!',
                libtcod.white)
            #Use blow strength as a max number of gibs
            rand_num_gibs = libtcod.random_get_int(0, 1, 7)
            for num in range(0, rand_num_gibs, 1):
                l = libtcod.random_get_float(0, 0, 1.0)
                color = libtcod.color_lerp(libtcod.darkest_red, libtcod.dark_red, l)
                #choose random spot for gibs
                x = libtcod.random_get_int(0, monster.x + 1, monster.x - 1)
                y = libtcod.random_get_int(0, monster.y + 1, monster.y - 1)
                if not is_blocked(x, y):
                    #roll for type of gib
                    roll = libtcod.random_get_int(0, 0, 3)
                    if roll == 0:
                        gib = Object(x, y, '%', 'guts', libtcod.darker_red, blocks=False,
                                     description='Remains of a squashed ' + str(monster.name) + '.')
                        libtcod.console_set_char_background(con, x, y, libtcod.dark_red, libtcod.BKGND_SET)
                        map[x][y].diff_color = libtcod.dark_red
                    if roll == 1:
                        gib = Object(x, y, "^", 'sinew', libtcod.dark_red, blocks=False,
                                     description='Remains of a squashed ' + str(monster.name) + '.')
                        libtcod.console_set_char_background(con, x, y, libtcod.darker_red, libtcod.BKGND_SET)
                        map[x][y].diff_color = libtcod.darker_red
                    if roll == 2:
                        gib = Object(x, y, '$', 'guts', libtcod.darker_purple, blocks=False,
                                     description='Remains of a squashed ' + str(monster.name) + '.')
                        libtcod.console_set_char_background(con, x, y, libtcod.darkest_red, libtcod.BKGND_SET)
                        map[x][y].diff_color = libtcod.darkest_red
                    if roll == 3:
                        gib = Object(x, y, '/', 'broken bone', libtcod.white, blocks=False,
                                     description='Remains of a squashed ' + str(monster.name) + '.')
                        libtcod.console_set_char_background(con, x, y, libtcod.dark_red, libtcod.BKGND_SET)
                        map[x][y].diff_color = libtcod.dark_red

                    #append gib and send it to back
                    objects.append(gib)
                    gib.send_to_back()

    message('The ' + monster.name.capitalize() + ' dies! You gain ' + str(monster.fighter.xp) + ' experience points.',
            libtcod.white)
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'Remains of ' + monster.name
    monster.send_to_back()


def target_tile(max_range=None):
    #return the position of a tile left-click in player's FOV (optionally in a range), or (None,None) if right clicked
    global key, mouse
    while True:
        #render the screen this erases the inventory and shows the names of objeects under the mouse
        libtcod.console_flush()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
        render_all()

        (x, y) = (mouse.cx, mouse.cy)

        if (mouse.lbutton_pressed and libtcod.map_is_in_fov(fov_map, x, y) and
                (max_range is None or player.distance(x, y) <= max_range)):
            return (x, y)

        if mouse.rbutton_pressed or key.vk == libtcod.KEY_ESCAPE:
            return (None, None)  #cancel if the player right clicks or presses escape


def target_monster(max_range=None):
    #returns a clicked monster inside FOV up to a range, or None if right-clicked
    while True:
        (x, y) = target_tile(max_range)
        if x is None:  #player cancelled
            return None

        #return the first clicked monster, otherwise continue looping
        for obj in objects:
            if obj.x == x and obj.y == y and obj.fighter and obj != player:
                return obj


def calc_border(x):
    border_len = []
    #For each step in the range of the msg_width(msg_stop), add one filler tile
    for i in range(0, x - 2, 1):
        border_len.append(BORDER_FILL)
    border = ''.join(border_len)

    border1 = BORDER_CORNER + border + BORDER_CORNER
    return border1


def new_game():
    global player, inventory, game_msgs, game_state, dungeon_level, turn_increment, turn_5, hunger_level, refresh_count

    key = libtcod.Key()
    #create object representing player
    fighter_component = Fighter(hp=100, defense_dice=2, defense_sides=2, power_dice=1, power_sides=2, evasion_dice=2, evasion_sides=1, accuracy_dice=1, accuracy_sides=5, xp=0, speed=10, death_function=player_death,
                                effects=[])
    player = Object(0, 0, '@', 'player', libtcod.lightest_amber, blocks=True, fighter=fighter_component)
    player.level = 1
    #Create the list of game messages and their colors, starts empty

    refresh_count = 0
    game_msgs = []
    inventory = []
    player_effects = []
    dungeon_level = 1
    TOTAL_XP = 0
    #counts turns up to 5 then resets
    turn_increment = 0
    #The number of sets of 5 turns that have occured, and been reset
    turn_5 = 0
    #hunger rate
    hunger_level = HUNGER_TOTAL
    #generate map
    make_map()
    initialize_fov()

    #This should eventuially be a one time if object.blocks = True and obj.fighter == None
    for obj in objects:
        if obj.name == 'Fountain':
            libtcod.map_set_properties(fov_map, obj.x, obj.y, True, False)

    for object in objects:
        if object.path is not None:
            object.path = None

    # Add an effect like this:

    #player.fighter.add_effect(Effect('Paralyzed', duration=5, paralyzed=True, base_duration=5), 'Game developer')
    #player.fighter.add_effect(Effect('cruelly hurt', duration=5, damage_by_turn=10), 'Game developer')
    #player.fighter.add_effect(Effect('Defense buffed', duration=50, defense_effect_dice=2, defense_effect_sides=2), 'Game developer')
    game_state = 'playing'


    #a warm welcoming message!
    message('Zeus is a dick! Go fuck him up.', libtcod.white)

    #initial equipment: a dagger
    equipment_component = Equipment(slot='left hand', power_bonus_dice=1, power_bonus_sides=1)
    obj = Object(0, 0, '-', 'wooden dagger', libtcod.darkest_orange, equipment=equipment_component,
                 description='A small wooden dagger, it provides a bonus to attack.')
    inventory.append(obj)
    equipment_component.equip()
    obj.always_visible = True


def initialize_fov():
    global fov_recompute, fov_map
    fov_recompute = True

    #create the FOV map, according to the generated map
    fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            libtcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)

    libtcod.console_clear(con)  # unexplored areas start black


def play_game():
    global key, mouse, turn_increment, heal_rate, fov_recompute, refresh_count

    player_action = None
    mouse = libtcod.Mouse()
    key = libtcod.Key()

    #Add elec
    elec = False
    if elec == True:
        player.fighter.add_effect(
            Effect(effect_name='electric power', mutation=True, applied_times=5, m_elec=True, m_elec_trigger=125,
                   m_elec_damage=150),
            'For your valiant effort you have earned the gods favour, they convene and offer you')
        elec = False

    ##MAIN LOOP##
    while not libtcod.console_is_window_closed():
        #render the screen
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
        render_all()

        libtcod.console_flush()

        #erase all objects at their old locations, before they move. Used to be after check_level_up
        #but moved to fix duplicate monster chars on floor

        #DISPLAY DAMAGE PAUSE
        for object in objects:
            if object.display_dmg != None:
                libtcod.sys_sleep_milli(50)
                fov_recompute = True
                object.display_dmg = None

        check_level_up()

        #this is where the re-write for speed needs to start

        #handles keys and exit game if needed
        player_action = handle_keys()

        #Run render_all() while the player does nothing to give flicker effect
        if player_action == 'didnt-take-turn':

            #Increase count
            refresh_count+=1
            #Trigger only after a certain number of didnt-take-turns
            if refresh_count >= 6:

                fov_recompute=True
                render_all()

                refresh_count = 0


        if player_action == 'exit':
            save_game()
            break

        #handle paralysis
        if player_action == 'paralyzed' and game_state == 'playing':
            check_by_turn(player.fighter.speed)
            check_run_effects(player)

        if player_action == 'moved' and game_state == 'playing':
            check_by_turn(player.fighter.speed)
            check_run_effects(player)

def shift_run(object, x, y):
    global fov_recompute
    #TODO: This is not rendering FOV each turn to check for monsters or to present it to root console.
    #Set a variable to check for in the while loop
    fov_danger = False
    #Create a count
    count = 0
    while fov_danger == False:


        #Trigger movement
        if count >= 5:
            #Move player
            object.move(x, y)
            #Loop for the players speed for his move
            check_by_turn(player.fighter.speed)

            #Render FOV and flush console
            fov_recompute=True
            render_all()
            libtcod.console_flush()


        #If is blocked, stop the run
        if is_blocked(object.x + x, object.y + y):
            #Set while variable to True to break the loop, should probably be a break
            fov_danger=True
            message('You cannot move any further.')

        #Check for monsters inside the players fov.
        for obj in objects:
            if libtcod.map_is_in_fov(fov_map, obj.x, obj.y) and obj.name != 'player' and obj.fighter and obj.fighter.hp > 0:
                message('You see a ' + str(obj.name) + '.')
                fov_danger=True

        #Increment the count
        count += 1

def main_menu():
    img = libtcod.image_load('zeus1.png')

    while not libtcod.console_is_window_closed():
        #show the background image, at twice the regular console resolution
        libtcod.image_blit_2x(img, 0, 0, 0)

        #show the game's title, and some credits
        libtcod.console_set_default_foreground(0, libtcod.black)
        libtcod.console_print_ex(0, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 4, libtcod.BKGND_NONE, libtcod.CENTER,
                                 'ZEUS MUST DIE')

        #show options and wait for the player's choice
        choice = menu('', ['Play a new game', 'Continue last game', 'Quit'], 24)

        if choice == 0:  #new game
            new_game()
            play_game()
        if choice == 1:  #load last game
            load_game()
            play_game()
        elif choice == 2:  #Quit
            break


def save_game():
    #open a new empty shelve (possibly overwriting an old one) to write the game data
    file = shelve.open('savegame', 'n')
    file['map'] = map
    file['objects'] = objects
    file['player_index'] = objects.index(player)  #index of player in objects list
    file['stairs_index'] = objects.index(stairs)
    file['inventory'] = inventory
    file['game_msgs'] = game_msgs
    file['game_state'] = game_state
    file['dungeon_level'] = dungeon_level
    file['hunger_level'] = hunger_level
    file['turn_increment'] = turn_increment
    file['turn_5'] = turn_5
    file['refresh_count'] = refresh_count

    file.close


def load_game():
    #open the previously saved shelve and load the game data
    global map, objects, player, inventory, game_msgs, game_state, stairs, dungeon_level, hunger_level, turn_increment, turn_5, refresh_count

    file = shelve.open('savegame', 'r')
    map = file['map']
    objects = file['objects']
    player = objects[file['player_index']]  # get index of player in objects list and access it
    stairs = objects[file['stairs_index']]
    inventory = file['inventory']
    game_msgs = file['game_msgs']
    game_state = file['game_state']
    dungeon_level = file['dungeon_level']
    hunger_level = file['hunger_level']
    turn_increment = file['turn_increment']
    turn_5 = file['turn_5']
    refresh_count = file['refresh_count']

    file.close()

    initialize_fov()


    #If the object used to have a path, make it None
    for object in objects:
        if object.path is not None:
            object.path = None


def next_level():
    global dungeon_level
    #advance to the next level
    message('Briefly crossing an unknown void, you feel a divine hand reach out and heal you.', libtcod.light_violet)
    player.fighter.heal(player.fighter.max_hp)  # heal player completely

    message('Fully healed, the world forms around you once again, and you continue your journey...', libtcod.red)
    dungeon_level += 1
    make_map()  # create a fresh new level!
    initialize_fov()


def check_level_up():
    #see if a players expereince is enough to level up
    level_up_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
    if player.fighter.xp >= level_up_xp:
        #it is! level up
        player.level += 1
        #TOTAL_XP += player.fighter.xp
        player.fighter.xp -= level_up_xp
        message('Your battle prowess grows! You have reached level ' + str(player.level) + '!', libtcod.yellow)
        choice = None
        while choice == None:  #keep asking until a choice is made
            render_all()
            choice = menu('Level up! Choose a stat to raise:\n',
                          ['Constitution (+20 HP)',
                           'Strength (+1 Attack)',
                           'Defense (+1 Defense)',
                           'Accuracy (+2 Accuracy, +1 Evasion)',
                           'Evasion (+2 Evasion, +1 Accuracy)'], LEVEL_SCREEN_WIDTH)

            # May be better to leave evasion and accuracy out of the players hands, to keep it simple
            if choice == 0:
                player.fighter.max_hp += 20
                player.fighter.hp += 20
            elif choice == 1:
                player.fighter.power += 1
            elif choice == 2:
                player.fighter.defense += 1
            elif choice == 3:
                player.fighter.acc += 2
                player.fighter.ev += 1
            elif choice == 4:
                player.fighter.ev += 2
                player.fighter.acc += 1

        #Add a random mutation
        level_mutate = (2, 7, 9, 12)
        for i in level_mutate:
            if player.level == i:
                #This will eventually be a pick a random mutation function
                player.fighter.add_effect(
                    Effect(effect_name='electric power', mutation=True, m_elec=True, m_elec_trigger=125,
                           m_elec_damage=150),
                    'For your valiant effort you have earned the gods favour, they convene and offer you')


def random_choice_index(chances):  #choose one option from list of chances, returning its index
    #the dice will land on some number between 1 and the sum of the chances
    dice = libtcod.random_get_int(0, 1, sum(chances))

    #go through all the chances, keeping the sum so far
    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w

        #see if the dice landed in the part thaty corresponds to this choice
        if dice <= running_sum:
            return choice
        choice += 1


def random_choice(chances_dict):
    #choose one option from a dictionary of chances, returning its key
    chances = chances_dict.values()  #Pull the integer value of a dict entry (80, 20, 10 etc.)
    strings = chances_dict.keys()  #Pull the string name of a dict entry (Dog/Snake etc)

    return strings[random_choice_index(chances)]  #return names[random function(specific value)]


def from_dungeon_level(table):
    #returns a value that depends on level. The table specifies what value occurs after each level, default is 0.
    for (value, level) in reversed(table):
        if dungeon_level >= level:
            return value
    return 0


#Handles turns/speed/heal
def check_by_turn(speed):
    global heal_rate, turn_increment, turn_5, hunger_level
    hunger_fire = 0
    for i in range(0, speed, 1):
        turn_increment += 1

        #Deal with hunger
        #Add one to the count
        hunger_fire += 1
        #If count is 2, decrease hunger by HUNGER_RATE
        if hunger_fire == 2:
            hunger_level -= HUNGER_RATE
            #Reset hunger_fire
            hunger_fire = 0

        #Iterate through objects list
        for obj in objects:

            #If the object is a fighter with a speed value
            if obj.fighter and obj.fighter.speed != None:

                #Increment the speed counter by 1
                obj.fighter.speed_counter += 1

                #Increment the heal rate by 1
                obj.fighter.heal_counter += 1

                #If the heal_counter == the heal_rate, heal by 1/100th of fighters hp
                if obj.fighter.heal_counter == obj.fighter.heal_rate:
                    heal = obj.fighter.max_hp / 100
                    obj.fighter.heal(heal)
                    #Reset counter to 0
                    obj.fighter.heal_counter = 0


                #If the speed value is equal to the speed counter
                if obj.fighter.speed_counter == obj.fighter.speed:

                    #Below are conditions for the turns mechanisms to fire an object

                    #If the object has an AI
                    if obj.ai:
                        obj.ai.take_turn()

                    #Reset speed counter
                    obj.fighter.speed_counter = 0

        #reset turn increment to 0 if it is 5, at the end of the function
        if turn_increment == 5:
            turn_increment -= 5
            turn_5 += 1

    if hunger_level <= 0:
        message('You are starving!', libtcod.light_red)
        player.fighter.take_damage(2)
        warning_count = 0


def total_turns():
    total_turns = turn_increment + (turn_5 * 5)
    return str(total_turns)


def hunger():
    #return string of hunger level (Full, Content, Peckish, Hungry, Starving)
    #TODO: make starving, v. hungry different colors
    global hunger_level
    increment = HUNGER_TOTAL / 5

    if hunger_level >= increment * 5:
        return 'Full'
    elif hunger_level >= increment * 4:
        return 'Content'
    elif hunger_level >= increment * 3:
        return 'Peckish'
    elif hunger_level >= increment * 2:
        return 'Hungry'
    elif hunger_level >= increment:
        return 'Very hungry'
    elif hunger_level >= 1:
        return 'Nearly starving'
    elif hunger_level <= 0:
        return 'Starving!'


def get_equipped_in_slot(slot):  #returns the equipment in a slot or None if it's empty
    for obj in inventory:
        if obj.equipment and obj.equipment.slot == slot and obj.equipment.is_equipped:
            return obj.equipment
    return None


def get_all_equipped(obj):  #returns a list of equipped items
    if obj == player:
        equipped_list = []
        for item in inventory:
            if item.equipment and item.equipment.is_equipped:
                equipped_list.append(item.equipment)
        return equipped_list
    else:
        return []  #TODO: other objects have no equipment, but if you gave them a simpler inventory system (no need for menu) they could drop equipped items, and have random ones spawn.


def iterate_through_list(x):
    list1 = []
    for i in x:
        list1.append('\n ' + str(i.owner.name).capitalize())
    #TODO: Use this line to print straight to panel2 with auto wrap rather than return a single string with \n's.
    #libtcod.console_print_rect_ex(panel2, 0, 0, PANEL_2_WIDTH, 1, libtcod.BKGND_NONE, libtcod.LEFT, header)
    return ' '.join(list1)


def add_bones(x, y):
    roll = libtcod.random_get_int(0, 0, 10)
    if roll >= 4:
        if not is_blocked(x, y):
            # create bones
            item_component = Item(use_function=None)
            item = Object(x, y, '%', 'Pile of bones', libtcod.lightest_grey, item=item_component, always_visible=True)
            num_bones = libtcod.random_get_int(0, 0, 5)
            for i in range(num_bones):
                # choose random spot for bones
                x = libtcod.random_get_int(0, item.x + 2, item.x - 2)
                y = libtcod.random_get_int(0, item.y + 2, item.y - 2)
                if not is_blocked(x, y):
                    #create other bones
                    item_component = Item(use_function=None)
                    xbones = Object(x, y, '%', 'Pile of bones', libtcod.lightest_grey, item=item_component,
                                    always_visible=True)
                    #append the bones
                    objects.append(xbones)
                    xbones.send_to_back()

            objects.append(item)
            item.send_to_back()


################
#INITIALISATION#
################
libtcod.console_set_custom_font("terminal8x12_gs_ro.png", libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/First RL', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
msgs = libtcod.console_new(MSG_WIDTH, PANEL_HEIGHT)
panel2 = libtcod.console_new(PANEL2_WIDTH, SCREEN_HEIGHT)
main_menu()

#To do:

#- MAJOR: Add conversation system for effects
#- MAJOR URGENT NEXT ISSUE: Maybe also implement scent tracking as well - http://codeumbra.eu/complete-roguelike-tutorial-using-c-and-libtcod-extra-3-scent-tracking

# - MAJOR, URGENT?: Implement ascii/tileset option, create artwork using that pixel editor


#- Decide on features needed for an alpha release to get feedback and playtesting. New menu/UI, a few more items, more monsters,
# some click to move functionality, skills (think sil) and mutations. Keep it simple, play tggw to get some idea of what
#is need for a release. Add new scrolls, new effects, fix evasion. Then work towards those features exclusively.
# Gotta fix that bread bug before a playable alpha.
#- Add new UI to right hand bar, one box for mouse over description, another for a list of enemies and their health bars
#with mouse-over-to-target functionality

