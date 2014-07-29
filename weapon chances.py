__author__ = 'PanicMechanic'

import libtcodpy as libtcod


def item_chances():
    rand_type = libtcod.random_get_int(0, 0, 5)  # Item types, starts at 0, weapons
    if rand_type == 0:  # Spawn a weapon
        #WEAPON CHANCES - Will have to be called each time for i in range
        item_chances = {}
        rand_weapon_type = libtcod.random_get_int(0, 0, 2)  # Weapon types, starts at 0, Swords,

        if rand_weapon_type == 0:  # Swords
            item_chances['wooden sword'] = from_dungeon_level([[5, 1], [10, 2]])
            item_chances['brass sword'] = from_dungeon_level([[5, 3], [10, 4]])
            item_chances['steel sword'] = from_dungeon_level([[1, 3], [10, 5]])
            item_chances['golden sword'] = from_dungeon_level([[5, 5], [10, 8]])
            item_chances['demon sword'] = from_dungeon_level([[1, 8], [2, 10]])
            item_chances['shining sword'] = from_dungeon_level([[1, 10], [2, 12]])
            item_chances['healing sword'] = from_dungeon_level([[1, 10], [1.5, 14]])

        if rand_weapon_type == 1:  # Axes
            item_chances['wooden axe'] = from_dungeon_level([[5, 1], [10, 2]])
            item_chances['bronze axe'] = from_dungeon_level([[5, 3], [10, 4]])
            item_chances['rusty steel axe'] = from_dungeon_level([[1, 3], [3, 5]])
            item_chances['steel axe'] = from_dungeon_level([[1, 3], [10, 5]])
            item_chances['diamond axe'] = from_dungeon_level([[5, 5], [10, 8]])
            item_chances['liberty axe'] = from_dungeon_level([[1, 8], [2, 10]])
            item_chances['ares axe'] = from_dungeon_level([[1, 10], [2, 12]])
            item_chances['godsbane axe'] = from_dungeon_level([[1, 10], [1.5, 14]])

        if rand_weapon_type == 2:  # War Hammers
            item_chances['wooden axe'] = from_dungeon_level([[5, 1], [10, 2]])
            item_chances['bronze axe'] = from_dungeon_level([[5, 3], [10, 4]])
            item_chances['rusty steel axe'] = from_dungeon_level([[1, 3], [3, 5]])
            item_chances['steel axe'] = from_dungeon_level([[1, 3], [10, 5]])
            item_chances['diamond axe'] = from_dungeon_level([[5, 5], [10, 8]])
            item_chances['liberty axe'] = from_dungeon_level([[1, 8], [2, 10]])
            item_chances['ares axe'] = from_dungeon_level([[1, 10], [2, 12]])
            item_chances['godsbane axe'] = from_dungeon_level([[1, 10], [1.5, 14]])

    if rand_type == 1:  # Spawn a piece of armor
        #ARMOR CHANCES - Will have to be called each time for i in range
        rand_armor_type = libtcod.random_get_int(0, 0, 2)  # Armor types, starts at 0, gauntlets
        if rand_armor_type == 0:  # gauntlets

            item_chances['silk gauntlets'] = from_dungeon_level([[5, 1], [10, 2]])
            item_chances['wooden gauntlets'] = from_dungeon_level([[5, 3], [10, 4]])
            item_chances['bronze gauntlets'] = from_dungeon_level([[1, 3], [10, 5]])
            item_chances['iron gauntlets'] = from_dungeon_level([[5, 5], [10, 8]])
            item_chances['steel gauntlets'] = from_dungeon_level([[1, 8], [2, 10]])
            item_chances['obsidian gauntlets'] = from_dungeon_level([[1, 10], [2, 12]])
            item_chances['Divine gauntlets'] = from_dungeon_level([[.10, 10], [1, 18]])

        if rand_weapon_type == 1:  # body armor
            item_chances['wooden armor'] = from_dungeon_level([[5, 1], [10, 2]])
            item_chances['bronze armor'] = from_dungeon_level([[5, 3], [10, 4]])
            item_chances['rusty steel armor'] = from_dungeon_level([[1, 3], [3, 5]])
            item_chances['steel armor'] = from_dungeon_level([[1, 3], [10, 5]])
            item_chances['diamond armor'] = from_dungeon_level([[5, 5], [10, 8]])
            item_chances['obsidian armor'] = from_dungeon_level([[1, 8], [2, 10]])
            item_chances['neptunes armor'] = from_dungeon_level([[1, 10], [2, 12]])
            item_chances['hercules armor'] = from_dungeon_level([[1, 10], [1.5, 14]])

        if rand_weapon_type == 2:  # helmets
            item_chances['wooden helmet'] = from_dungeon_level([[5, 1], [10, 2]])
            item_chances['bronze helmet'] = from_dungeon_level([[5, 3], [10, 4]])
            item_chances['rusty steel helmet'] = from_dungeon_level([[1, 3], [3, 5]])
            item_chances['steel helmet'] = from_dungeon_level([[1, 3], [10, 5]])
            item_chances['diamond helmet'] = from_dungeon_level([[5, 5], [10, 8]])
            item_chances['obsidian helmet'] = from_dungeon_level([[1, 8], [2, 10]])
            item_chances['hermes helmet'] = from_dungeon_level([[1, 10], [2, 12]])
            item_chances['hades helmet'] = from_dungeon_level([[1, 10], [1.5, 14]])

    if rand_type == 2:  # Spawn a wearable item
        #W/Item CHANCES - Will have to be called each time for i in range
        rand_item_type = libtcod.random_get_int(0, 0, 2)  # W/Item types, starts at 0, rings
        if rand_item_type == 0:  # rings

            item_chances['wooden ring of health'] = from_dungeon_level([[50, 1], [100, 5]])
            item_chances['wooden ring of power'] = from_dungeon_level([[50, 1], [100, 5]])
            item_chances['wooden ring of defense'] = from_dungeon_level([[50, 1], [100, 5]])
            item_chances['steel ring of health'] = from_dungeon_level([[50, 5], [100, 8]])
            item_chances['steel ring of power'] = from_dungeon_level([[50, 5], [100, 8]])
            item_chances['steel ring of defense'] = from_dungeon_level([[50, 5], [100, 8]])
            item_chances['golden ring of health'] = from_dungeon_level([[30, 8], [60, 12]])
            item_chances['golden ring of power'] = from_dungeon_level([[30, 8], [60, 12]])
            item_chances['golden ring of defense'] = from_dungeon_level([[30, 8], [60, 12]])
            item_chances['diamond ring of health'] = from_dungeon_level([[15, 12], [30, 15]])
            item_chances['diamond ring of power'] = from_dungeon_level([[15, 12], [30, 15]])
            item_chances['diamond ring of defense'] = from_dungeon_level([[15, 12], [30, 15]])
            item_chances['glowing ring of health'] = from_dungeon_level([[5, 15]])
            item_chances['glowing ring of power'] = from_dungeon_level([[5, 15]])
            item_chances['glowing ring of defense'] = from_dungeon_level([[5, 15]])

        if rand_weapon_type == 1:  # amulets
            item_chances['wooden armor'] = from_dungeon_level([[5, 1], [10, 2]])
            item_chances['bronze armor'] = from_dungeon_level([[5, 3], [10, 4]])
            item_chances['rusty steel armor'] = from_dungeon_level([[1, 3], [3, 5]])
            item_chances['steel armor'] = from_dungeon_level([[1, 3], [10, 5]])
            item_chances['diamond armor'] = from_dungeon_level([[5, 5], [10, 8]])
            item_chances['obsidian armor'] = from_dungeon_level([[1, 8], [2, 10]])
            item_chances['neptunes armor'] = from_dungeon_level([[1, 10], [2, 12]])
            item_chances['hercules armor'] = from_dungeon_level([[1, 10], [1.5, 14]])

        if rand_weapon_type == 2:  # belt
            item_chances['wooden helmet'] = from_dungeon_level([[5, 1], [10, 2]])
            item_chances['bronze helmet'] = from_dungeon_level([[5, 3], [10, 4]])
            item_chances['rusty steel helmet'] = from_dungeon_level([[1, 3], [3, 5]])
            item_chances['steel helmet'] = from_dungeon_level([[1, 3], [10, 5]])
            item_chances['diamond helmet'] = from_dungeon_level([[5, 5], [10, 8]])
            item_chances['obsidian helmet'] = from_dungeon_level([[1, 8], [2, 10]])
            item_chances['hermes helmet'] = from_dungeon_level([[1, 10], [2, 12]])
            item_chances['hades helmet'] = from_dungeon_level([[1, 10], [1.5, 14]])

def rand_weapon():#would need to take int account dungeon level

    rw = Object(x, y, char, name, color, equipment=None, item=None, always_visible=True)
    rand_type = libtcod.random_get_int(0, 0, 2)  # Weapon types, starts at 0, Swords,
    if rand_weapon_type == 0:  # Swords
        rw.char = '/'
        #bad swords
        sword_names_0 = [leather, wax, cloth, childrens, broken, clay]
        #acceptable swords
        sword_names_1 = [wooden, stone, rusted]
        #average swords
        sword_names_2 = [bronze, iron]
        #good swords
        sword_names_3 = [steel, ]

def create_weapon():
    weapon_type = libtcod.random_get_int(0, 0, 3)
    if weapon_type = 0:
        rand_weapon().rw

    weapon_chances['heal'] = 15  # healing potion always shows up, even if all other items have 0 chance
    weapon_chances['bread'] = 8  # bread always shows up, even if all other items have 0 chance


weapon_chances['wooden plate armor'] = from_dungeon_level([[2, 2], [15, 5]])
weapon_chances['wooden sword'] = from_dungeon_level([[5, 1], [10, 2]])
weapon_chances['wooden shield'] = from_dungeon_level([[10, 2], [10, 2]])
