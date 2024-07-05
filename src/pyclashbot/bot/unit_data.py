import pandas as pd


class Unit:
    def __init__(self, name, cost, card_type, attack_type):
        self.name = name  # str
        self.cost = cost  # int
        self.card_type = (
            card_type  # ['melee', 'ranged', 'turret', 'spawner','spell','hog','mortar']
        )
        self.attack_type = attack_type
        # [single, splash, tower, turret, tower_attacker,
        # mortar, spawner,tower_attacking_spell,anti_cluster]

    def __repr__(self):
        return f"Unit(name={self.name}, cost={self.cost}, card_type={self.card_type}, attack_type={self.attack_type})"

    def print_unit(self):
        print('{:^20} : {:^3} : {:^15} : {:^19}'.format(self.name,self.cost,self.card_type,self.attack_type))


units = []

# tank_type units
units.append(Unit("lava_hound", 7, "tank_type", "tower"))
units.append(Unit("elixir_golem", 3, "tank_type", "tower"))
units.append(Unit("giant_regular", 5, "tank_type", "tower"))
units.append(Unit("e_giant", 7, "tank_type", "tower"))
units.append(Unit("goblin_giant", 6, "tank_type", "tower"))
units.append(Unit("golem", 8, "tank_type", "tower"))
units.append(Unit("ice_golem", 2, "tank_type", "tower"))
# hog_type units
units.append(Unit("wall_breakers", 2, "hog_type", "tower"))
units.append(Unit("skeleton_barrel", 3, "hog_type", "tower"))
units.append(Unit("battle_ram", 4, "hog_type", "tower"))
units.append(Unit("balloon", 5, "hog_type", "tower"))
units.append(Unit("ram_rider", 5, "hog_type", "tower"))
units.append(Unit("royal_hogs", 5, "hog_type", "tower"))
units.append(Unit("hog_rider", 4, "hog_type", "tower"))
units.append(Unit("royal_giant", 5, "hog_type", "tower"))
# mortar_type units
units.append(Unit("xbow", 6, "mortar_type", "mortar"))
units.append(Unit("mortar", 4, "mortar_type", "mortar"))
# melee_type units
units.append(Unit("skeleton_king", 4, "melee_type", "splash"))
units.append(Unit("phoenix", 4, "melee_type", "single"))
units.append(Unit("royal_delivery", 2, "melee_type", "splash"))
units.append(Unit("bandit", 3, "melee_type", "single"))
units.append(Unit("barbarians", 5, "melee_type", "single"))
units.append(Unit("bats", 2, "melee_type", "single"))
units.append(Unit("dark_prince", 4, "melee_type", "splash"))
units.append(Unit("e_spirit", 1, "melee_type", "splash"))
units.append(Unit("skeletons", 1, "melee_type", "single"))
units.append(Unit("fire_spirit", 1, "melee_type", "splash"))
units.append(Unit("healer", 4, "melee_type", "single"))
units.append(Unit("elite_barbarians", 6, "melee_type", "single"))
units.append(Unit("minions", 3, "melee_type", "single"))
units.append(Unit("giant_skeleton", 6, "melee_type", "single"))
units.append(Unit("ice_spirit", 1, "melee_type", "single"))
units.append(Unit("knight", 3, "melee_type", "single"))
units.append(Unit("mega_minion", 3, "melee_type", "single"))
units.append(Unit("valkyrie", 4, "melee_type", "splash"))
units.append(Unit("goblins", 2, "melee_type", "single"))
units.append(Unit("golden_knight", 4, "melee_type", "splash"))
units.append(Unit("guards", 3, "melee_type", "single"))
units.append(Unit("heal_spirit", 1, "melee_type", "splash"))
units.append(Unit("minion_horde", 5, "melee_type", "single"))
units.append(Unit("lumberjack", 4, "melee_type", "single"))
units.append(Unit("royal_recruits", 7, "melee_type", "single"))
units.append(Unit("mega_knight", 7, "melee_type", "splash"))
units.append(Unit("skeleton_army", 3, "melee_type", "single"))
units.append(Unit("mighty_miner", 4, "melee_type", "single"))
units.append(Unit("mini_pekka", 4, "melee_type", "single"))
units.append(Unit("monk", 5, "melee_type", "single"))
units.append(Unit("pekka", 7, "melee_type", "single"))
units.append(Unit("_prince", 5, "melee_type", "single"))
units.append(Unit("rascals", 5, "melee_type", "single"))
units.append(Unit("royal_ghost", 3, "melee_type", "splash"))
# ranged_type units
units.append(Unit("witch", 5, "ranged_type", "splash"))
units.append(Unit("bowler", 5, "ranged_type", "splash"))
units.append(Unit("night_witch", 4, "ranged_type", "single"))
units.append(Unit("goblin_gang", 3, "ranged_type", "single"))
units.append(Unit("hunter", 4, "ranged_type", "splash"))
units.append(Unit("cannon_cart", 5, "ranged_type", "single"))
units.append(Unit("goblin_demolisher", 4, "ranged_type", "splash"))
units.append(Unit("dart_goblin", 3, "ranged_type", "single"))
units.append(Unit("e_wizard", 4, "ranged_type", "single"))
units.append(Unit("executioner", 5, "ranged_type", "splash"))
units.append(Unit("firecracker", 3, "ranged_type", "splash"))
units.append(Unit("three_musketeers", 7, "ranged_type", "single"))
units.append(Unit("fisherman", 3, "ranged_type", "single"))
units.append(Unit("ice_wizard", 3, "ranged_type", "splash"))
units.append(Unit("magic_archer", 4, "ranged_type", "splash"))
units.append(Unit("mother_witch", 4, "ranged_type", "splash"))
units.append(Unit("musketeer", 4, "ranged_type", "single"))
units.append(Unit("princess", 3, "ranged_type", "splash"))
units.append(Unit("skeleton_dragons", 4, "ranged_type", "splash"))
units.append(Unit("sparky", 6, "ranged_type", "single"))
units.append(Unit("spear_goblins", 2, "ranged_type", "single"))
units.append(Unit("wizard", 5, "ranged_type", "splash"))
units.append(Unit("archer_queen", 5, "ranged_type", "single"))
units.append(Unit("inferno_dragon", 4, "ranged_type", "single"))
units.append(Unit("e_dragon", 5, "ranged_type", "splash"))
units.append(Unit("little_prince", 3, "ranged_type", "single"))
units.append(Unit("zappies", 4, "ranged_type", "single"))
units.append(Unit("archers", 3, "ranged_type", "single"))
units.append(Unit("baby_dragon", 4, "ranged_type", "splash"))
units.append(Unit("bomber", 2, "ranged_type", "splash"))
units.append(Unit("flying_machine", 4, "ranged_type", "single"))
# turret_type
units.append(Unit("goblin_cage", 4, "turret_type", "turret"))
units.append(Unit("tesla", 4, "turret_type", "turret"))
units.append(Unit("bomb_tower", 4, "turret_type", "turret"))
units.append(Unit("cannon_tower", 3, "turret_type", "turret"))
units.append(Unit("inferno_tower", 5, "turret_type", "turret"))
# miner_type
units.append(Unit("miner", 3, "miner_type", "tower_attacker"))
units.append(Unit("graveyard", 5, "miner_type", "tower_attacker"))
units.append(Unit("goblin_drill", 4, "miner_type", "tower_attacker"))
# spawner_type
units.append(Unit("furnace", 4, "spawner_type", "spawner"))
units.append(Unit("tombstone", 3, "spawner_type", "spawner"))
units.append(Unit("goblin_hut", 5, "spawner_type", "spawner"))
units.append(Unit("barbarian_hut", 6, "spawner_type", "spawner"))
units.append(Unit("elixir_collector", 6, "spawner_type", "spawner"))
# spell_type
units.append(Unit("freeze", 4, "spell_type", "anti_cluster"))
units.append(Unit("log", 2, "spell_type", "anti_cluster"))
units.append(Unit("lightning", 6, "spell_type", "tower_attacking_spell"))
units.append(Unit("arrows", 3, "spell_type", "anti_cluster"))
units.append(Unit("barbarian_barrel", 2, "spell_type", "anti_cluster"))
units.append(Unit("tornado", 3, "spell_type", "anti_cluster"))
units.append(Unit("poison", 4, "spell_type", "anti_cluster"))
units.append(Unit("earthquake", 3, "spell_type", "anti_cluster"))
units.append(Unit("fireball", 4, "spell_type", "anti_cluster"))
units.append(
    Unit("clone", 3, "spell_type", "anti_cluster")
)  # who knows what to do with this card
units.append(Unit("rocket", 6, "spell_type", "tower_attacking_spell"))
units.append(Unit("snowball", 2, "spell_type", "anti_cluster"))
units.append(Unit("rage", 2, "spell_type", "anti_cluster"))
units.append(Unit("zap_spell", 2, "spell_type", "anti_cluster"))


# assemble the list of units into a dataframe going card_name, cost,card_type
unit_df = pd.DataFrame(
    [(unit.name, unit.cost, unit.card_type, unit.attack_type) for unit in units],
    columns=["card_name", "cost", "card_type", "attack_type"],
)


def get_units(
    cost=None, card_type=None, attack_type=None, min_cost=None, max_cost=None, card_names_only=True
):
    query = []

    if cost is not None:
        query.append(f"cost == {cost}")
    if card_type is not None:
        query.append(f"card_type == '{card_type}'")
    if attack_type is not None:
        query.append(f"attack_type == '{attack_type}'")
    if min_cost is not None:
        query.append(f"cost >= {min_cost}")
    if max_cost is not None:
        query.append(f"cost <= {max_cost}")

    if query:
        query_str = " & ".join(query)
        filtered_df = unit_df.query(query_str)
    else:
        filtered_df = unit_df

    if card_names_only:
        return filtered_df['card_name'].tolist()
    else:
        return [
            Unit(row.card_name, row.cost, row.card_type, row.attack_type)
            for idx, row in filtered_df.iterrows()
        ]


if __name__ == "__main__":
    units = get_units(max_cost=3, card_type="melee_type",attack_type='splash')
    for unit in units:
        unit.print_unit()
