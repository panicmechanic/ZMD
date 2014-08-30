import libtcodpy as libtcod
import weaponchances


def random_monster():

    #chance of each monsters
    monster_chances = {}
    monster_chances['Dog'] = 30  #Dog always spawns, even if all other monsters have 0 chance
    monster_chances['Snake'] = weaponchances.from_dungeon_level([[3, 1], [5, 3], [50, 7]])
    monster_chances['Imp'] = weaponchances.from_dungeon_level([[50, 2], [30, 5], [50, 7]])
    monster_chances['Firefly'] = weaponchances.from_dungeon_level([[3, 1], [30, 3], [60, 7]])
    monster_chances['Crab'] = weaponchances.from_dungeon_level([[1, 2], [30, 3], [60, 7]])
    monster_chances['Goat'] = weaponchances.from_dungeon_level([[15, 2], [30, 8], [60, 10]])
    monster_chances['Eagle'] = weaponchances.from_dungeon_level([[15, 5], [30, 8], [60, 10]])
    monster_chances['Pygmy'] = weaponchances.from_dungeon_level([[10, 5], [40, 8], [50, 10]])
    monster_chances['Bull'] = weaponchances.from_dungeon_level([[10, 6], [40, 7], [10, 9]])
    monster_chances['Centaur'] = weaponchances.from_dungeon_level([[5, 6], [20, 7], [30, 9]])

    return monster_chances

def create_monster(x, y):
    monster_chances = random_monster()
    choice = weaponchances.random_choice(monster_chances)

    if choice == 'Dog':
        #create an dog
        fighter_component = Fighter(hp=10, defense_dice=1, defense_sides=5, power_dice=1, power_sides=8, evasion_dice=1, evasion_sides=4, accuracy_dice=2, accuracy_sides=4, xp=400, speed=10,
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
