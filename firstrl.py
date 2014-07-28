import libtcodpy as libtcod
import math
import textwrap
import shelve
import pdb

#actual size of the window
SCREEN_WIDTH = 130
SCREEN_HEIGHT = 60

#size of the map
MAP_WIDTH = 130
MAP_HEIGHT = 53

#parameters for dungeon generator
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 35


#sizes and coordinates relevant for GUI
BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1
INVENTORY_WIDTH = 50
LEVEL_SCREEN_WIDTH = 40
CHARACTER_SCREEN_WIDTH = 30

#FOV
FOV_ALGO = 0 #Default FOV algorithm
FOV_LIGHT_WALLS = True #Light walls or not
TORCH_RADIUS = 10

#Item parameters
HEAL_AMOUNT = 40
LIGHTNING_DAMAGE = 40
LIGHTNING_RANGE = 5
CONFUSE_NUM_TURNS = 10
CONFUSE_RANGE = 8
FIREBALL_RADIUS = 3
FIREBALL_DAMAGE = 25
heal_rate = 1

#Food properties
FOOD_BREAD = 380
HUNGER_RATE = 1.5

#Player parameters
LEVEL_UP_BASE = 200
LEVEL_UP_FACTOR = 200

#FPS
LIMIT_FPS = 20  #20 frames-per-second maximum

#Player effects
POISON_TURN = 0
POISON_COUNTDOWN = 0
POISON_DURATION = 0

#TODO: NEED TO CHANGE THESE VALUES AT SOME POINT, MAYBE AFTER NOISE SYSTEM
color_dark_wall = libtcod.Color(120, 90, 55)
color_light_wall = libtcod.Color(150, 120, 85)
color_dark_ground = libtcod.Color(110, 110, 110)
color_light_ground = libtcod.Color(130, 130, 130)

class Tile:
	# a tile of the map, and its properties
	def __init__(self, blocked, block_sight = None):
		self.blocked = blocked
		
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
 	def __init__(self, x, y, char, name, color, equipment=None, effects=None, blocks=False, always_visible=False, fighter=None, ai=None, item=None, description=None, seen=False, path=None, decorative=False):
		self.x = x
		self.y = y
		self.char = char
		self.name = name
		self.color = color
		self.blocks = blocks
		self.always_visible = always_visible
		self.fighter = fighter
		if self.fighter: #let the fighter component know who owns it
			self.fighter.owner = self
		
		self.ai = ai
		if self.ai: #let the ai component know who owns it
			self.ai.owner = self
		
		self.item = item
		if self.item: #let the item component know who owns it, like a bitch
			self.item.owner = self
		
		self.equipment = equipment
		if self.equipment: #let the equipment component know who owns it
			self.equipment.owner = self
			
			#there must be an Item component for the Equipment component to work properly
			self.item = Item()
			self.item.owner = self
			
		self.effects = effects
		if self.effects:#let the effect component know who owns it
			self.effects.owner = self
			
			#there must be a fighter component for the effect component to work properly
			self.fighter = Fighter()
			self.fighter.owner = self
					
		self.description = self
		self.seen = seen
		self.path = path
		self.decorative = decorative
			
	def move(self, dx, dy):
		#move by the given amount, if the destination is not blocked
		if not is_blocked(self.x + dx, self.y + dy):
			self.x += dx
			self.y += dy
			
	def move_towards(self, target_x, target_y):
		#vector from this object to the target, and distance
		dx = target_x - self.x
		dy = target_y - self.y
		distance = math.sqrt(dx ** 2 + dy ** 2)
		
		#normalise it to 1 length (preserving direction), then round it and
		#convert to integer so the movement is restricted to the map grid
		dx = int(round(dx / distance))
		dy = int(round(dy / distance))
		self.move(dx, dy)
		
	def distance_to(self, other):
		#return the distance to another object
		dx = other.x - self.x
		dy = other.y - self.y
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
	def __init__(self, hp, defense, power, xp, ev, death_function=None, effects = [], poison=0):
		self.base_max_hp = hp
		self.hp = hp
		self.base_defense = defense
		self.base_power = power
		self.xp = xp
		self.ev = ev
		self.death_function = death_function
		self.effects = effects
		self.poison = poison
		
	
	@property
	def power(self): #return actual power, by summing up the bonuses from all equipped items
		bonus = (sum(equipment.power_bonus for equipment in get_all_equipped(self.owner))) + (sum(effect.power_effect for effect in self.effects))
		return self.base_power + bonus
	
	@property
	def defense(self): #return actual defense, by summing up the bonuses from all equipped items
		bonus = sum(equipment.defense_bonus for equipment in get_all_equipped(self.owner))
		return self.base_defense + bonus
		
	@property
	def max_hp(self): #return actual max_hp, by summing up the bonuses from all equipped items
		bonus = sum(equipment.max_hp_bonus for equipment in get_all_equipped(self.owner))
		return self.base_max_hp + bonus
	
	
	def take_damage(self, damage):
		#apply damage if possible
		percentage_to_hit = libtcod.random_get_int(0, 0, 100)
		if damage > 0: #and percentage_to_hit > self.ev:#TODO: need to create a better system to account for a skill with a weapon class and critical hits and message for missed hits on both players and monsters
			self.hp -= damage
					
		#check for death, if there's a death function, call it.
		if self.hp <=0:
			function = self.death_function
			if function is not None:
				function(self.owner)
			
			if self.owner != player: #yield experience to the player
				player.fighter.xp += self.xp
			
	def attack(self, target):
		#a simple formula for attack damage
		damage = self.power - target.fighter.defense
		
		if damage > 0:
			#make the target take some damage
			message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
			target.fighter.take_damage(damage)
		else:
			message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')
	
	def heal(self, amount):
		#heal by the given amount, without going over the maximum
		self.hp += amount
		if self.hp > self.max_hp:
			self.hp = self.max_hp
	
class BasicMonster:
	global path
	#AI for a basic monster.
	def take_turn(self):
		#a basic monster takes its turn. If you can see it, it can see you.
		monster = self.owner
		#check for existing path
		if monster.path == None:
			monster.path = libtcod.path_new_using_map(fov_map,1.41)
			
		if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
		
			#move towards player if far away
			if monster.distance_to(player) >= 2:
				#compute how to reach the player
				libtcod.path_compute(monster.path, monster.x, monster.y, player.x, player.y)
				#and move one tile towards them
				nextx, nexty = libtcod.path_walk(monster.path,True)
				monster.move_towards(nextx, nexty)
				check_run_effects(monster)
			#close enough, attack! (if the player is still alive.)
			elif player.fighter.hp > 0:
				monster.fighter.attack(player)
				
				#poison if attack is by snake 
				roll = libtcod.random_get_int(0, 0, 10)
				if monster.char == 's' and roll >= 7:
					player.fighter.poison=1
		
		else:
			#the player cannot see the monster
			#if we have an old path, follow it
			#this means monsters will always move to where they last saw you
			if not libtcod.path_is_empty(monster.path):
				nextx, nexty = libtcod.path_walk(monster.path,True)
				monster.move_towards(nextx, nexty)
			#stop boar and baby boars and pygmys from wandering
			elif not monster.char == 'B' or monster.char == 'b' or monster.char == 'p':
				#path is empty, wander randomly
				rand_direction = libtcod.random_get_int(0, 1, 8)
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
				else:
					monster.move(1, -1)
			else:
				return 'cancelled'
			
class ConfusedMonster:
	#AI for a temporarily confused monster, reverts to normal AI after a while
	def __init__(self, old_ai, num_turns=CONFUSE_NUM_TURNS):
		self.old_ai = old_ai
		self.num_turns = num_turns
		
	def take_turn(self):
		if self.num_turns > 0: #still confused...
			#move in a random direction, and decrease the number of turns confused
			self.owner.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
			self.num_turns -= 1
		else: #restore the previous AI (this one will be deleted because it's not referenced anymore)
			self.owner.ai = self.old_ai
			message('The ' + self.owner.name + ' is no longer confused!', libtcod.red)
	
			
	
			
class Item:
	#An item that can be picked up and used
	def __init__(self, use_function=None):
		self.use_function = use_function
		
		
	def use(self):
		#special case: if the object has the Equipment component, the "use" action is to equip/dequip
		if self.owner.equipment:
			self.owner.equipment.toggle_equip()
			return
		#just call the "use function" if it is defined
		if self.use_function is None:
			message('The ' + self.owner.name + ' cannot be used.')
		else:
			if self.use_function() != 'cancelled':
				inventory.remove(self.owner) #destroy after use, unless it was cancelled for some reason
				
	
	def pick_up(self):
		#add to the player's inventory and remove from the map
		if len(inventory) >=26:
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
	def __init__(self, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0):
		self.power_bonus = power_bonus
		self.defense_bonus = defense_bonus
		self.max_hp_bonus = max_hp_bonus
		
		self.slot = slot
		self.is_equipped = False
		
	def toggle_equip(self): #toggle equip/dequip status
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
	def __init__(self, effect_name, duration=0, turns_passed=0, power_effect=0, defense_effect=0, max_hp_effect=0, confused=False, burning=False):
		self.effect_name = effect_name
		self.duration = duration
		self.turns_passed = turns_passed
		self.power_effect = power_effect
		self.defense_effect = defense_effect
		self.max_hp_effect = max_hp_effect
		self.confused = confused
		self.burning = burning
		
		self.is_active = False
	
	def add_effect(Fighter): # If the effect has a name, add it to the fighter class's list of effects
		if self.effect_name is not None:
			self.effects.append(self.owner)
	
	def remove_effect(self):
		if duration == turns_passed:
			self.effects.remove(self.owner)
			

def apply_effect(self, effect, targetx, targety,):#must apply the effect component from the object to a target fighter.
	for obj in objects:
		if obj.x == targetx and obj.y == targety:
			obj.fighter.effects.append(effect)
		else:
			print 'No target found'
	
def check_run_effects(obj):#Check for effects, if theere is one increase its turn_passed value by one, if it is equal to duration remove it.
	if obj.effects is not None:
		for eff in effects:
			if turns_passed is not duration:
				turns_passed += 1
			elif turns_passed == duration:
				remove_effect(eff)
	else:
		return 'no effects'
				
	
def number_of_turns():
	global turn_increment, turn_5
	turns = turn_increment + (turn_5 * 5)
	return turns
		
def count_turns(turn_duration):#Returns a true value when no_of_turns has passed
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
	
	#chance of each monsters
	monster_chances = {}
	monster_chances['Dog'] = 80 #Dog always spawns, even if all other monsters have 0 chance
	monster_chances['Snake'] = from_dungeon_level([[5, 2], [30, 5], [50, 7]])
	monster_chances['Imp'] = from_dungeon_level([[15, 1], [30, 5], [50, 7]])
	monster_chances['Firefly'] = from_dungeon_level([[10, 2], [30, 3], [60, 7]])
	monster_chances['Crab'] = from_dungeon_level([[10, 2], [30, 3], [60, 7]])
	monster_chances['Goat'] = from_dungeon_level([[15, 2], [30, 8], [60, 10]])
	monster_chances['Eagle'] = from_dungeon_level([[15, 5], [30, 8], [60, 10]])
	monster_chances['Pygmy'] = from_dungeon_level([[10, 5], [40, 8], [50, 10]])
	monster_chances['Bull'] = from_dungeon_level([[10, 6], [40, 7], [10, 9]])
	monster_chances['Centaur'] = from_dungeon_level([[5, 6], [20, 7], [30, 9]])
	
	#maximum number of items per room
	max_items = from_dungeon_level([[1, 1], [2, 4], [3, 6]])
	
	#chance of each item (by default they have a chance of 0 at level 1, which then goes up)
	item_chances = {}
	item_chances['heal'] = 15 #healing potion always shows up, even if all other items have 0 chance
	item_chances['bread'] = 8 #bread always shows up, even if all other items have 0 chance
	item_chances['lightning'] = from_dungeon_level([[25, 4]])
	item_chances['fireball'] = from_dungeon_level([[25, 6]])
	item_chances['confuse'] = from_dungeon_level([[10, 2]])
	item_chances['bones'] = from_dungeon_level([[70, 1]])
	item_chances['wooden sword'] = from_dungeon_level([[5, 1], [10 ,2]])
	item_chances['wooden shield'] = from_dungeon_level([[10, 2], [10, 2]]) 
	item_chances['brass sword'] = from_dungeon_level([[5, 3], [10, 4]]) 
	item_chances['steel sword'] = from_dungeon_level([[2, 3], [10, 5]]) 
	item_chances['wooden plate armor'] = from_dungeon_level([[2, 2], [15, 5]]) 
	
	#choose random number of monsters
	num_monsters = libtcod.random_get_int(0, 0, max_monsters)
	
	#center coordinates of new room for placing bosses
	(new_x, new_y) = room.center()
	
	for i in range(num_monsters):
		#choose random spot for this monster
		x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
		y = libtcod.random_get_int(0, room.y1+1, room.y2-1)
		
		#only place it if a tile is not blocked
		if not is_blocked(x, y):
			choice = random_choice(monster_chances)
			if choice == 'Dog': 
				#create an dog
				fighter_component = Fighter(hp=20, defense=0, power=4, xp=35, ev=10, death_function=monster_death)
				ai_component = BasicMonster()				
				monster = Object(x, y, 'd', 'Dog', libtcod.darker_orange, blocks=True, fighter=fighter_component, ai=ai_component, description='A big angry dog')	
			
			elif choice == 'Snake': 
				#create a Snake
				fighter_component = Fighter(hp=30, defense=3, power=5, xp=100, ev=2, death_function=monster_death)
				ai_component = BasicMonster()				
				monster = Object(x, y, 's', 'Snake', libtcod.darker_grey, blocks=True, fighter=fighter_component, ai=ai_component, description='A big angry dog')
			
			elif choice == 'Imp': 
				#create an Imp
				fighter_component = Fighter(hp=15, defense=1, power=4, xp=50, ev=99, death_function=monster_death)
				ai_component = BasicMonster()
				monster = Object(x, y, 'i', 'Imp', libtcod.darker_green, blocks=True, fighter=fighter_component, ai=ai_component, description='A big angry dog')
			
			elif choice == 'Eagle':
				#create an eagle
				fighter_component = Fighter(hp=40, defense=3, power=10, xp=200, ev=20, death_function=monster_death)
				ai_component = BasicMonster()
				monster = Object(x, y, 'e', 'Eagle', libtcod.darker_sepia, blocks=True, fighter=fighter_component, ai=ai_component, description='A big angry dog')
				
			elif choice == 'Firefly':
				#create a glow fly
				fighter_component = Fighter(hp=8, defense=0, power=8, xp=50, ev=20, death_function=monster_death)
				ai_component = BasicMonster()
				monster = Object(x, y, 'f', 'Firefly', libtcod.darker_lime, blocks=True, fighter=fighter_component, ai=ai_component, description='A big angry dog')
			
			elif choice == 'Pygmy':
				#create a pygmy
				fighter_component = Fighter(hp=30, defense=4, power=4, xp=200, ev=20, death_function=monster_death)
				ai_component = BasicMonster()
				monster = Object(x, y, 'p', 'Pygmy', libtcod.dark_pink, blocks=True, fighter=fighter_component, ai=ai_component, description='A big angry dog')
				#Generate random number of baby boars
				num_pygmys = libtcod.random_get_int(0, 1, 6)
				for i in range(num_pygmys):
					#choose random spot for baby boars
					x = libtcod.random_get_int(0, monster.x+2, monster.x-2)
					y = libtcod.random_get_int(0, monster.y+2, monster.y-2)
					if not is_blocked(x, y):
						#create other pygmys
						fighter_component = Fighter(hp=30, defense=4, power=4, xp=200, ev=20, death_function=monster_death)
						ai_component = BasicMonster()				
						other_pygmy = Object(x, y, 'p', 'Pygmy', libtcod.dark_pink, blocks=True, fighter=fighter_component, ai=ai_component, description='A baby boar, how cute.')
						#append the little fuckers
						objects.append(other_pygmy)
			
			elif choice == 'Goat':
				#create a goat
				fighter_component = Fighter(hp=35, defense=3, power=5, xp=60, ev=20, death_function=monster_death)
				ai_component = BasicMonster()
				monster = Object(x, y, 'g', 'Goat', libtcod.lighter_grey, blocks=True, fighter=fighter_component, ai=ai_component, description='A big angry dog')
			
			elif choice == 'Bull':
				#create a bull
				fighter_component = Fighter(hp=80, defense=1, power=8, xp=250, ev=20, death_function=monster_death)
				ai_component = BasicMonster()
				monster = Object(x, y, chr(208), 'Bull', libtcod.light_flame, blocks=True, fighter=fighter_component, ai=ai_component, description='A big angry dog')
			
			elif choice == 'Crab':
				#create a crab
				fighter_component = Fighter(hp=30, defense=4, power=5, xp=50, ev=20, death_function=monster_death)
				ai_component = BasicMonster()
				monster = Object(x, y, 'c', 'Crab', libtcod.dark_yellow, blocks=True, fighter=fighter_component, ai=ai_component, description='A big angry dog')
			
			elif choice == 'Centaur':
				#create a centaur
				fighter_component = Fighter(hp=100, defense=7, power=10, xp=300, ev=20, death_function=monster_death)
				ai_component = BasicMonster()
				monster = Object(x, y, 'C', 'Centaur', libtcod.darker_magenta, blocks=True, fighter=fighter_component, ai=ai_component, description='A big angry dog')
			
			
			objects.append(monster)
			
		
	#choose random number of items
	num_items = libtcod.random_get_int(0, 0, max_items)
	
	for i in range(num_items):
		#choose random spot for this item
		x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
		y = libtcod.random_get_int(0, room.y1+1, room.y2-1)
		
		#only place it if the tile is not blocked
		if not is_blocked(x, y):
			choice = random_choice(item_chances)
			
			if choice == 'heal':
				#create a healing potion
				item_component = Item(use_function=cast_heal)
				item = Object(x, y, chr(173), 'healing potion', libtcod.dark_green, item=item_component, always_visible=True)
			
			elif choice == 'lightning':
				#create a lightning bolts scroll (15% chance)
				item_component = Item(use_function=cast_lightning)
				item = Object(x, y, '!', 'scroll of lightning bolt', libtcod.light_blue, item=item_component, always_visible=True)
			
			elif choice == 'fireball':
				#create a fireball scroll (10% chance)
				item_component = Item(use_function=cast_fireball)
				item = Object(x, y, '#', 'scroll of fireball', libtcod.dark_orange, item=item_component, always_visible=True)
			
			elif choice == 'confuse':
				#create a confuse scroll (15% chance)
				item_component = Item(use_function=cast_confuse)
				item = Object(x, y, '?', 'scroll of confusion', libtcod.darkest_yellow, item=item_component, always_visible=True)
			elif choice == 'bread':
				#create a piece of bread
				item_component = Item(use_function=(eat_food(200)))
				item = Object(x, y, 'x', 'piece of bread', libtcod.darkest_red, item=item_component, always_visible=True)
			
			elif choice == 'bones':#TODO: Need to create decorative item class, could do cool stuff, also make dead obdies appear over obnes
				#create bones
				item_component = Item(use_function=None)
				item = Object(x, y, '%', 'Pile of bones', libtcod.lightest_grey, item=item_component, always_visible=False)
				num_bones = libtcod.random_get_int(0, 0, 5)
				for i in range(num_bones):
					#choose random spot for bones
					x = libtcod.random_get_int(0, item.x+2, item.x-2)
					y = libtcod.random_get_int(0, item.y+2, item.y-2)
					if not is_blocked(x, y):
						#create other bones
						item_component = Item(use_function=None)
						xbones = Object(x, y, '%', 'Pile of bones', libtcod.lightest_grey, item=item_component, always_visible=False)
						#append the bones
						objects.append(xbones)
						xbones.send_to_back()
						
			elif choice == 'wooden sword':#TODO: Equipment classes, wooden, iron, steel. Randomised from levels 
											#(maybe borrow code from chance generation in place_items to pick a liklihood for an item type to spawn
				#create a sword
				equipment_component = Equipment(slot='right hand', power_bonus=4)
				item = Object(x, y, '/', 'Wooden sword', libtcod.darker_orange, equipment=equipment_component, item=None, always_visible=True)
				
			elif choice == 'wooden shield':
				#create a wooden shield
				equipment_component = Equipment(slot='left hand', defense_bonus=2)
				item = Object(x, y, '[', 'Wooden shield', libtcod.darker_orange, equipment=equipment_component, item=None, always_visible=True)
				
			elif choice == 'brass sword':
				#create a brass sword
				equipment_component = Equipment(slot='right hand', power_bonus=6)
				item = Object(x, y, '/', 'Brass sword', libtcod.brass, equipment=equipment_component, item=None, always_visible=True)
					
			elif choice == 'steel sword':
				#create a steel sword
				equipment_component = Equipment(slot='right hand', power_bonus=8)
				item = Object(x, y, '/', 'Steel sword', libtcod.silver, equipment=equipment_component, item=None, always_visible=True)
				
			elif choice == 'wooden plate armor':
				#create a wooden plate armor
				equipment_component = Equipment(slot='body', defense_bonus=2)
				item = Object(x, y, chr(234), 'Wooden plate armor', libtcod.darkest_orange, equipment=equipment_component, item=None, always_visible=True)
			
			objects.append(item)
			
			item.send_to_back() #items appear below other objects

def place_special_rooms():#TODO: Redo the dungeon generation to allow for special rooms, or ensure v_tun and h_tun will not intersect special room
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
		decx = new_x-2
		decy = new_y+10
		#place objects in room:
		for x in range(9):
			decy -= 2
			decoration = Object(decx, decy, chr(159), 'Fountain', libtcod.lighter_blue, blocks=False, decorative=True)
			objects.append(decoration)
		decx = new_x+2
		decy = new_y+10
		for x in range(9):
			decy -= 2
			decoration = Object(decx, decy, chr(159), 'Fountain', libtcod.lighter_blue, blocks=False, decorative=True)
			objects.append(decoration)
			
		
		
		
			
def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
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
	libtcod.console_print_ex(panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER, name + ': ' + str(value) + '/' + str(maximum))

def get_names_under_mouse():
	global mouse

	#return a string with the names of all objects under the mouse
	(x, y) = (mouse.cx, mouse.cy)
	
	#create a list with the names of all objects at the mouse's coordinates and in FOV
	names = [obj.name for obj in objects if obj.x == x and obj.y == y and libtcod.map_is_in_fov(fov_map, obj.x, obj.y)]
	
	names = ', '.join(names) #join the names, seperated by commas
	return names.capitalize()
	
def description_menu(header): #TODO: THIS NEEDS TO BE FINISHED

	global mouse
	
	#return a string with the names of all objects under the mouse
	(x, y) = (mouse.cx, mouse.cy)
	
	#create a list with the names of all objects at the mouse's coordinates and in FOV
	names = [obj for obj in objects if obj.x == x and obj.y == y and libtcod.map_is_in_fov(fov_map, obj.x, obj.y) and obj.description is not None]
	
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
	map = [[ Tile(True)
		for y in range(MAP_HEIGHT) ]
			for x in range(MAP_WIDTH) ]
			
	rooms = []

	num_rooms = 0
	
	place_special_rooms()
	
	for r in range(MAX_ROOMS):
		#random width and height
		w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
		h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
		#random position without going out of the boundaries of the map
		x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
		y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)
	
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
				(prev_x, prev_y) = rooms[num_rooms-1].center()
			
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
			num_rooms += 1
	
	#create stairs at the center of the last room
	stairs = Object(new_x, new_y, '>', 'stairs', libtcod.white, always_visible=True)
	objects.append(stairs)
	stairs.send_to_back() # so it's drawn below the monsters
	
	#Roll for boss and create if roll >= 7
	roll = libtcod.random_get_int(0, 0, 10)
	if roll >= 6 and dungeon_level == 2:
		boar_mother(new_x, new_y)
	
def boar_mother(x, y):
	global map, rooms
	fighter_component = Fighter(hp=35, defense=2, power=6, xp=400, ev=20, death_function=monster_death)
	ai_component = BasicMonster()
	boar = Object(x, y, 'B', 'Giant Boar Mother', libtcod.darker_red, blocks=True, fighter=fighter_component, ai=ai_component, description='A big angry ')
	#Generate random number of baby boars
	num_babies = libtcod.random_get_int(0, 15, 35)
	#append boar before it is used to generate babies
	objects.append(boar)
	for i in range(num_babies):
		#choose random spot for baby boars
		x = libtcod.random_get_int(0, boar.x+2, boar.x-2)
		y = libtcod.random_get_int(0, boar.y+2, boar.y-2)
		if not is_blocked(x, y):
			#create baby boars
			fighter_component = Fighter(hp=2, defense=0, power=3, xp=5, ev=1, death_function=monster_death)
			ai_component = BasicMonster()				
			monster = Object(x, y, 'b', 'Baby boar', libtcod.darkest_red, blocks=True, fighter=fighter_component, ai=ai_component, description='A baby boar, how cute.')
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
	x = SCREEN_WIDTH/2 - width/2
	y = SCREEN_HEIGHT	/2 - height/2
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
	
def inventory_menu(header):#TODO: Find a way to sit all copies of an item into a single option and present it, adjusting the value of the option by -1 if chosen
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
	#healing_potion = 0
	#for 'healing potion' in inventory:
	#	healing_potion += 1
	
def msgbox(text, width=50):
	menu(text, [], width) #use menu() as a sort of "message box"
	
def render_all():
	global fov_map, color_dark_wall, color_light_wall
	global color_dark_ground, color_light_ground
	global fov_recompute
	global objects
	global turn
		
	if fov_recompute:
		#recompute FOV if needed (the player moved or something)
		fov_recompute = False
		libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)
	
		#go through all tiles and set their background color
		for y in range(MAP_HEIGHT):
			for x in range(MAP_WIDTH):
				visible = libtcod.map_is_in_fov(fov_map, x, y)
				wall = map[x][y].block_sight
				if not visible: 
					#if it's not explored right now, the player can only see it if it's explored
					if map[x][y].explored:
						if wall:
							libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET)
						else:
							libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET)
				else:
					#it's visible
					if wall: 
						libtcod.console_set_char_background(con, x, y, color_light_wall, libtcod.BKGND_SET )
					else:
						libtcod.console_set_char_background(con, x, y, color_light_ground, libtcod.BKGND_SET )
					#since it's visible, explore it
					map[x][y].explored = True
	
	#draw all objects in list, except the player, want it to always appear on top, so we draw it later
	for object in objects:
		if object != player:
			object.draw()
	player.draw()
	
	#blit the contents of "con" to root console and present it
	libtcod.console_blit(con, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, 0, 0)

	#prepare to render the GUI panel
	libtcod.console_set_default_background(panel, libtcod.black)
	libtcod.console_clear(panel)
	
	#print the game messages, one line at a time
	y = 1
	for (line, color) in game_msgs:
		libtcod.console_set_default_foreground(panel, color)
		libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
		y += 1
	
	#show the player's stats
	render_bar(1, 1, BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp, libtcod.light_red, libtcod.darker_red)
	libtcod.console_print_ex(panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT, 'Dungeon level ' + str(dungeon_level))
	libtcod.console_print_ex(panel, 1, 5, libtcod.BKGND_NONE, libtcod.LEFT, 'Hunger:' + str(hunger()))
	
	
	#display names of objects under the mouse
	libtcod.console_set_default_foreground(panel, libtcod.light_gray)
	libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse())
		
	#blit the contents of "panel" to the root console
	libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)

def wait_for_spacekey():#Make cast heal message appear without having to press the same key twice
	libtcod.console_flush()
	key = libtcod.console_wait_for_keypress(True)
	choice = None
	while choice == None: #keep asking until a choice is made
		if key.vk == libtcod.KEY_SPACE:
			choice = 'space'
			return 'cancelled'
			#check for keypress, render and flush the screen to present monster inside fov.
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)
		
		
		
	
def message_wait(char, messagetext, color = libtcod.white):
	#display message once when char comes into FOV then set seen to true
	for object in objects:
		if object.char == char and libtcod.map_is_in_fov(fov_map, object.x, object.y) and object.seen == False:
			render_all()
			#use message function to present message
			message(messagetext, color)
			render_all()#IF THIS FUNCTION IS THE CAUSE OF A CRASH REMOVE THIS LINE AND GO FUCK YOURSELF
			#set object to seen
			object.seen = True
			#wait for keypress
			key = libtcod.console_wait_for_keypress(True)
			
			choice = None
			
			while choice == None: #keep asking until a choice is made
				if key.vk == libtcod.KEY_SPACE:
					choice == 'space'
					return 'cancelled'
				#check for keypress, render and flush the screen to present monster inside fov.
				libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)
				render_all()
		
				libtcod.console_flush()
		
			

	
def message(new_msg, color = libtcod.white):#TODO: Why can't this function end with render_all()?
	#split the message if necessary, among multiple lines
	new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)
	

	for line in new_msg_lines:
		#if the buffer is full, remove the first line to make room for the new one
		if len(game_msgs) == MSG_HEIGHT:
			del game_msgs[0]
			
		#add the new line as a tuple, with the text and the color
		game_msgs.append( (line, color) )
		
def player_move_or_attack(dx, dy):
	global fov_recompute
	
	#the coordinates the player is moving to/attacking
	x = player.x + dx
	y = player.y + dy
	
	#try to find an attackable object there
	target = None
	for object in objects:
		if object.fighter and object.x == x and object.y == y:
			target = object
			break
	
	#attack if target found, move otherwise
	if target is not None:
		player.fighter.attack(target)
	else:
		player.move(dx, dy)
		fov_recompute = True
	
	
	
def handle_keys():
	global keys;
	
	if key.vk == libtcod.KEY_ENTER and key.lalt:
		#Alt + Enter toggle fullscreen
		libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
		
	elif key.vk == libtcod.KEY_ESCAPE:
		return 'exit' #Exit game
	
	if game_state == 'playing':
	#movement keys
		if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
			player_move_or_attack(0, -1)
			return 'moved'
		elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
			player_move_or_attack(0, 1)
			return 'moved'
		elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
			player_move_or_attack(-1, 0)
			return 'moved'
		elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
			player_move_or_attack(1, 0)
			return 'moved'
		elif key.vk == libtcod.KEY_HOME or key.vk == libtcod.KEY_KP7:
			player_move_or_attack(-1, -1)
			return 'moved'
		elif key.vk == libtcod.KEY_PAGEUP or key.vk == libtcod.KEY_KP9:
			player_move_or_attack(1, -1)
			return 'moved'
		elif key.vk == libtcod.KEY_END or key.vk == libtcod.KEY_KP1:
			player_move_or_attack(-1, 1)
			return 'moved'
		elif key.vk == libtcod.KEY_PAGEDOWN or key.vk == libtcod.KEY_KP3:
			player_move_or_attack(1, 1)
			return 'moved'
		elif key.vk == libtcod.KEY_KP5:
			pass #do nothing ie wait for the monster to come to you
			return 'moved'
		else:
			#test for other keys
			key_char = chr(key.c)
			
			if key_char == 'g':
				#pick up an item
				for object in objects: #look for an item in the players tile
					if object.x == player.x and object.y == player.y and object.item and object.char is not '%':
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
				cast_heal()
				
			#debug	
			if key_char == ']':
				for y in range(MAP_HEIGHT):
					for x in range(MAP_WIDTH):
						map[x][y].explored = True
			
			if key_char == 'd':
				#show the inventory; if an item is selected, drop it.
				chosen_item = inventory_menu('Press the key next to an item to drop it, or any other to canel.\n')
				if chosen_item is not None:
					chosen_item.drop()
					
			if key_char == 'D':#TODO: Fix this bullsheet
				#show the description menu, if an item is selected, describe it.
				chosen_object = description_menu('Press the key next to an object to see its description.\n')
				if chosen_object is not None:
					message(str(chosen_object.description), libtcod.white)
				
					
			if key_char == '>':
				#go down stairs, if the player is on them
				if stairs.x == player.x and stairs.y == player.y:
					next_level()	

			if key_char == 'c':
				level_up_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
				msgbox('Character Information\n\nLevel: ' + str(player.level) + '\nExperience: ' + str(player.fighter.xp) +
					'\nExperience to level up: ' + str(level_up_xp) + '\n\nHP: ' + str(player.fighter.max_hp) +
					'\nAttack: ' + str(player.fighter.power) + '\nDefense: ' + str(player.fighter.defense), CHARACTER_SCREEN_WIDTH)
						
			return 'didnt-take-turn'
			
def closest_monster(max_range):
	#find closest enemy, up to a maximum range, and in the players FOV
	closest_enemy = None
	closest_dist = max_range + 1 #start with slightly more than max range
	
	for object in objects:
		if object.fighter and not object == player and libtcod.map_is_in_fov(fov_map, object.x, object.y):
			#calculate distance between this object and the player
			dist = player.distance_to(object)
			if dist < closest_dist: # it's closer so remember it
				closest_enemy = object
				closest_dist = dist
	return closest_enemy
			
def cast_heal():
	#heal the player
	if player.fighter.hp == player.fighter.max_hp:
		message('You are already at full health.', libtcod.red)
		return 'cancelled'
	else:
		message('Your wounds pulse with a magical energy, some bind and close entirely! Press SPACE to continue.', libtcod.light_violet)
		player.fighter.heal(HEAL_AMOUNT)
		render_all()
		wait_for_spacekey()

def eat_food(value):
	#TODO: Allow system to call objects food value if any, and restore by that amount
	#currently only allows for a fixed rate for one type of food
	global hunger_level
	#Lower their hunger level
	
	if hunger_level <= 40:
		message('You are already full!', libtcod.white)
		return 'cancelled'
	else:
		message('Mmm, that was delicious!', libtcod.light_green)
		hunger_level -= value
		

def cast_lightning():
	#find nearest enemy (inside a maximum range) and damage it
	monster = closest_monster(LIGHTNING_RANGE)
	if monster is None: #no enemy found within maximum range
		message ('No enemy is close enough to strike.', libtcod.red)
		return 'cancelled'
		
	#Zap it like it's hot!
	message('A lightning bolt thunders from the scroll with a loud clap and strikes the ' + monster.name + ' for ' + str(LIGHTNING_DAMAGE) + ' hit points. Press SPACE to continue.', libtcod.light_blue)
	monster.fighter.take_damage(LIGHTNING_DAMAGE)
	render_all()
	wait_for_spacekey()
	
def cast_confuse():
	#ask the player for a target to confuse
	message('Left-lick to target an enemy and confuse it, right-click to cancel.', libtcod.light_cyan)
	monster = target_monster(CONFUSE_RANGE)
	if monster is None: return 'cancelled'
		
	old_ai = monster.ai
	monster.ai = ConfusedMonster(old_ai)
	monster.ai.owner = monster #tell the compnent who owns it
	message('You hear Dionysus laugh maniacally, the ' + monster.name + ' is touched by the god and becomes confused! Press SPACE to continue.', libtcod.light_green)
	render_all()
	wait_for_spacekey()
	
def cast_fireball():#FIGURE OUT HOW TO PAUSE AFTER THIS MESSAGE BEFORE DEALING DAMAGE
	#ask the player for a target tile to throw a fireball at
	message('Lef-click a target tile for the fireball, or right_click to cancel.', libtcod.light_cyan)
	(x, y) = target_tile()
	if x is None: return 'cancelled'
	message('Hephaestus turns his crippled body to you from an unseen dimension, and the air surrounding you explodes in a violent fireball! Press SPACE to continue.', libtcod.orange)
	render_all()
	wait_for_spacekey()
	
	for obj in objects: #damage every fighter in range, including the player
		if obj.distance(x, y) <= FIREBALL_RADIUS and obj.fighter and obj != player:
			message('The ' + obj.name + ' is completely immolated and loses ' + str(FIREBALL_DAMAGE) + ' hit points.', libtcod.orange)
			obj.fighter.take_damage(FIREBALL_DAMAGE)
					
def player_death(player):
	#the game ended!
	global game_state
	message('You died! Zeus will continue his rampage.', libtcod.red)
	game_state = 'dead'
	
	#for added effect, transform the player into a corpse!
	player.char = '%'
	player.color = libtcod.dark_red

def monster_death(monster):
	#transform it into a nasty corpse! it doesn't block, can't be attacked and doesn't move.
	message('The ' + monster.name.capitalize() + ' dies! You gain ' + str(monster.fighter.xp) + ' experience points.', libtcod.orange)
	monster.char = '%'
	monster.color = libtcod.dark_red
	monster.blocks = False
	monster.fighter = None
	monster.ai = None
	monster.name = 'remains of ' + monster.name
	monster.send_to_back()

	
def target_tile(max_range=None):
	#return the position of a tile left-click in player's FOV (optionally in a range), or (None,None) if right clicked
	global key, mouse
	while True:
		#render the screen this erases the inventory and shows the names of objeects under the mouse
		libtcod.console_flush()
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)
		render_all()
		
		(x, y) = (mouse.cx, mouse.cy)
		
		if (mouse.lbutton_pressed and libtcod.map_is_in_fov(fov_map, x, y) and 
		(max_range is None or player.distance(x, y) <= max_range)):
			return (x, y)
			
			
		if mouse.rbutton_pressed or key.vk == libtcod.KEY_ESCAPE:
			return (None, None) #cancel if the player right clicks or presses escape
			
def target_monster(max_range=None):
	#returns a clicked monster inside FOV up to a range, or None if right-clicked
	while True:
		(x, y) = target_tile(max_range)
		if x is None: #player cancelled
			return None
			
		#return the first clicked monster, otherwise continue looping
		for obj in objects:
			if obj.x == x and obj.y == y and obj.fighter and obj != player:
				return obj
				
def new_game():
	global player, inventory, game_msgs, game_state, dungeon_level, turn_increment, heal_rate, turn_5, hunger_level
	#create object representing player
	fighter_component = Fighter(hp=100, defense=1, power=2, xp=0, ev=20, death_function=player_death)
	player = Object(0, 0, '@', 'player', libtcod.white, blocks=True, fighter=fighter_component)
	player.level = 1
	#Create the list of game messages and their colors, starts empty
	game_msgs = []
	inventory = []
	player_effects = []
	dungeon_level = 1
	#counts turns up to 5 then resets
	turn_increment = 0
	#The number of sets of 5 turns that have occured, and been reset
	turn_5 = 0
	#hunger rate
	hunger_level = 0
	#generate map
	make_map()
	initialize_fov()
	
	game_state = 'playing'
	
	
	#a warm welcoming message!
	message('Zeus has killed Great Alexander in a fit of jealousy! He flees to the top of Mt. Olympus, give chase, and claim your retribution!', libtcod.red)

	#initial equipment: a dagger
	equipment_component = Equipment(slot='right hand', power_bonus=2)
	obj = Object(0, 0, '-', 'wooden dagger', libtcod.darkest_orange, equipment=equipment_component)
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

	libtcod.console_clear(con) # unexplored areas start black		
			
def play_game():
	global key, mouse, turn_increment, heal_rate
		
	player_action = None
	mouse = libtcod.Mouse()
	key = libtcod.Key()
	##MAIN LOOP##
	while not libtcod.console_is_window_closed():

	#render the screen
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)
		render_all()
		
		libtcod.console_flush()
		
		check_level_up()
		
		#check for message wait conditions
		message_wait('B', 'You see an enormous hairy boar and what appear to be her offspring, she looks angry! Press SPACE to continue..', libtcod.red)
		
		
		
		#erase all objects at their old locations, before they move
		for object in objects:
			object.clear()
		
		#handles keys and exit game if needed
		player_action = handle_keys()
		if player_action == 'exit':
			save_game()
			break
		if player_action == 'moved':
			check_by_turn()
			check_run_effects(player)
			
		
		
		#let monsters take their turn
		if game_state == 'playing' and player_action != 'didnt-take-turn':
			for object in objects:
				if object.ai:
					object.ai.take_turn()
					
			
		
def main_menu():
	roll = libtcod.random_get_int(0, 0, 12)
	if roll >= 6:
		img = libtcod.image_load('zeus1.png')
	else:
		img = libtcod.image_load('zeus.png')
	
	while not libtcod.console_is_window_closed():
		#show the background image, at twice the regular console resolution
		libtcod.image_blit_2x(img, 0, 0, 0)
		
		#show the game's title, and some credits
		libtcod.console_set_default_foreground(0, libtcod.black)
		libtcod.console_print_ex(0, SCREEN_WIDTH/2, SCREEN_HEIGHT/2-4, libtcod.BKGND_NONE, libtcod.CENTER, 'ZEUS MUST DIE')
		libtcod.console_print_ex(0, SCREEN_WIDTH/2, SCREEN_HEIGHT-2, libtcod.BKGND_NONE, libtcod.CENTER, 'By Johnson Spink')

		#show options and wait for the player's choice
		choice = menu('', ['Play a new game', 'Continue last game', 'Quit'], 24)
		
		if choice == 0: #new game
			new_game()
			play_game()
		if choice == 1: #load last game
			try:
				load_game()
			except:
				msgbox('\n No saved game to load. \n', 24)
				continue
			play_game()
		elif choice == 2: #Quit
			break
			
def save_game():
	#open a new empty shelve (possibly overwriting an old one) to write the game data
	file = shelve.open('savegame', 'n')
	file['map'] = map
	file['objects'] = objects
	file['player_index'] = objects.index(player) #index of player in objects list
	file['stairs_index'] = objects.index(stairs)
	file['inventory'] = inventory
	file['game_msgs'] = game_msgs
	file['game_state'] = game_state	
	file['dungeon_level'] = dungeon_level
	file['hunger_level'] = hunger_level
	file['turn_increment'] = turn_increment
	file['turn_5'] = turn_5
	
	file.close

def load_game():
	#open the previously saved shelve and load the game data
	global map, objects, player, inventory, game_msgs, game_state, stairs, dungeon_level, hunger_level, turn_increment, turn_5
	
	file = shelve.open('savegame', 'r')
	map = file['map']
	objects = file['objects']
	player = objects[file['player_index']]# get index of player in objects list and access it
	stairs = objects[file['stairs_index']]
	inventory = file['inventory']
	game_msgs = file['game_msgs']
	game_state = file['game_state']
	dungeon_level = file['dungeon_level']
	hunger_level = file['hunger_level']
	turn_increment = file['turn_increment']
	turn_5 = file['turn_5']
	
	file.close()
	
	initialize_fov()
	
def next_level():
	global dungeon_level
	#advance to the next level
	message('Briefly crossing an unknown void, you feel a divine hand reach out and heal you.', libtcod.light_violet)
	player.fighter.heal(player.fighter.max_hp) # heal player completely
	
	message('Fully healed, the world forms around you once again, you continue your journey...', libtcod.red)
	dungeon_level += 1
	make_map() # create a fresh new level!
	initialize_fov()
	
def check_level_up():#TODO: Add cool mutations to fighter class like horns
	#see if a players expereince is enough to level up
	level_up_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
	if player.fighter.xp >= level_up_xp:
		#it is! level up
		player.level += 1
		player.fighter.xp -= level_up_xp
		message('Your battle prowess grows! You have reached level ' + str(player.level) + '!', libtcod.yellow)
		choice = None
		while choice == None: #keep asking until a choice is made
			choice = menu('Level up! Choose a stat to raise:\n',
				['Constitution (+20 HP, from ' + str(player.fighter.max_hp) + ')',
				'Strength (+1 Attack, from ' + str(player.fighter.power) + ')',
				'Agility (+1 Defense, from ' + str(player.fighter.defense) + ')'], LEVEL_SCREEN_WIDTH)
				
			if choice == 0:
				player.fighter.max_hp += 20
				player.fighter.hp += 20
			elif choice == 1:
				player.fighter.power += 1
			elif choice == 2:
				player.fighter.defense += 1
				
def random_choice_index(chances):#choose one option from list of chances, returning its index
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
	chances = chances_dict.values()#Pull the integer value of a dict entry (80, 20, 10 etc.)
	strings = chances_dict.keys()#Pull the string name of a dict entry (Dog/Snake etc)
	
	return strings[random_choice_index(chances)] #return names[random function(specific value)]

def from_dungeon_level(table):
	#returns a value that depends on level. The table specifies what value occurs after each level, default is 0.
	for (value, level) in reversed(table):
		if dungeon_level >= level:
			return value
	return 0

def check_by_turn():
	global heal_rate, turn_increment, turn_5, hunger_level, POISON_COUNTDOWN, POISON_DURATION
	turn_increment += 1
	if turn_increment == 5:
		player.fighter.heal(heal_rate)
		turn_increment -= 5
		turn_5 += 1
		
	#Take care of the hunger variables here, may be better in their own function
	if hunger_level < 200:
		hunger_level += HUNGER_RATE
	elif hunger_level == 800:
		message('You are starving!', libtcod.light_red)
		player.fighter.take_damage(1)
	
	#TODO: Create eventy class with poison function
	if player.fighter.poison >= 1 or POISON_COUNTDOWN >= 1:
		#each instance of poison is 3 turns worth of damage
		if player.fighter.poison >= 1:
			message('You have been poisoned', libtcod.light_green)
			POISON_DURATION = (player.fighter.poison * 4)
			player.fighter.poison = 0
		if POISON_DURATION is not 0:
			POISON_COUNTDOWN += POISON_DURATION
			POISON_DURATION = 0
		POISON_COUNTDOWN -= 1
		player.fighter.take_damage(2)
		
def total_turns():
	total_turns = turn_increment + (turn_5 * 5)
	return str(total_turns)
	
def hunger():
	#return string of hunger level (Full, Content, Peckish, Hungry, Starving)
	#TODO: make starving, v. hungry different colors
	global hunger_level
	if hunger_level <= 80:
		return 'Full'
	elif hunger_level <= 240:	
		return 'Content'
	elif hunger_level <= 400:	
		return 'Peckish'
	elif hunger_level <= 560:
		return 'Hungry'
	elif hunger_level <= 799:
		return 'Very hungry'
	elif hunger_level == 800:
		return 'Starving!'
		
def get_equipped_in_slot(slot): #returns the equipment in a slot or None if it's empty
	for obj in inventory:
		if obj.equipment and obj.equipment.slot == slot and obj.equipment.is_equipped:
			return obj.equipment
	return None

		

def get_all_equipped(obj): #returns a list of equipped items
	if obj == player:
		equipped_list = []
		for item in inventory:
			if item.equipment and item.equipment.is_equipped:
				equipped_list.append(item.equipment)
		return equipped_list
	else:
		return [] #TODO: other objects have no equipment, but if you gave them a simpler inventory system (no need for menu) they could drop equipped items, and have random ones spawn.
		
	
##############################
#INITIALISATION AND MAIN LOOP#		
##############################	
libtcod.console_set_custom_font("terminal8x12_gs_ro.png", libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/First RL', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
main_menu()


	

#Done so far:
#- Implemented singular boss system (will do for now)
#- Implemented message_wait system for discoveries the player needs to pay attention to. Currently displays on second loop.
#- Half implemented describe feature
#- Implement hunger system! Food still buggy  so only one type right now.
#- Implemented poison feature
#- Implemented wait for space key feature
#- Give monsters proper pathfinding.
#- Implemented space to continue after scroll messages
#- Created see all map debug key
#- Created special room function, but is not seperated from the map because v+h_tunnel does not check for intersection
#
#To do:
#- Fix evasion
#- Mouse over + right click describe feature
#- Add mutations n shit
#- Fix the description feature
#- Add a monster.drop_item system to drop shit like gnoll tooth which you need for quests etc.
#- Need to create decorative item class, could do cool stuff
#- MAJOR: Create new map() functions for different terrain types
#- MAJOR: Add attack types (slash, stab, crush, etc.)  for weapon classes.
#- MAJOR: Add conversation system for events
#- MAJOR URGENT: Add an effect class that can be applied to monsters in the same way equipment class was made.
#- MAJOR URGENT NEXT ISSUE: Maybe also implement scent tracking as well - http://codeumbra.eu/complete-roguelike-tutorial-using-c-and-libtcod-extra-3-scent-tracking
#- MAJOR URGENT NEXT ISSUE: Levels 1-4 are the same, add more monsters and items to help you deal with the new monsters. It can't be one wooden shield and sword for 4 levels.
#- Add monsters, items, equipment
#- Add high score page at main menu based off total xp
#- MOST MAJOR URGENT PROBLEM: Event class and how to implement it. Fuck me. What a nightmare. Maybe write a drawing to lay it out
#- Figure out how to change the walls to objects with a char.
#- Implement mouse pathfinding - click to move.
#- Figure out why pathfinding is not loading properly, probably a value isn't being saved.
#- MAJOR: Turn system http://www.roguebasin.com/index.php?title=A_simple_turn_scheduling_system_--_Python_implementation