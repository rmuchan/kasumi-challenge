import json

from .GameChar import numerical
from .rand import randomize
from .util import recurrence


def boss_gen(template: dict, lv):
    rating = [0, 0]
    boss = randomize(template, rating)
    boss['attack'] = attack_calc(boss['attack'], lv)
    boss['defence'] = boss['defence_base'] + lv * boss['defence_grow']
    del boss['defence_base'], boss['defence_grow']
    boss['HP'] = hp_calc(boss['hp_base'], boss['life_base'], lv)
    del boss['hp_base'], boss['life_base']
    boss['recover_rate'] = boss['recover_rate'] * rates_3_calc(lv)
    boss['spell_rate'] = boss['spell_rate'] * rates_3_calc(lv)
    boss['buff_rate'] = boss['buff_rate'] * rates_3_calc(lv)
    boss['power_rating'] = rating[0] * 2 / rating[1]
    boss['exp_earn'] = boss['power_rating'] * exp_earn_calc(lv)
    return boss


def attack_calc(atk, lv):
    return recurrence(atk, numerical['attr_rate'], atk*0.02, lv)


def hp_calc(hp_base, life_base, lv):
    add = recurrence(life_base, numerical['attr_rate'], life_base * 0.02, lv)
    return (recurrence(add, numerical['attr_rate'], add * 0.021, lv) + hp_base) * numerical['hp_rate']


def rates_3_calc(lv):
    virtual_attr = recurrence(numerical['per_base'], numerical['attr_rate'], numerical['per_grow'], lv)
    return numerical['enhance_constant'] * (virtual_attr ** numerical['enhance_exponent'])


# 击败这个怪物会获得这么多经验
def exp_earn_calc(lv: int):
    current = numerical['exp_earn_base']
    for _ in range(lv - 1):
        current = current * numerical['exp_earn_rate'] + numerical['exp_earn_add']
    return current


if __name__ == '__main__':
    with open('./data/boss-pool/magician.json') as FILE:
        boss_json = json.load(FILE)
    for i in [1,10,20,30]:
        print(boss_gen(boss_json, i))

"""
    "name": "魔法师",
    "is_player": false,
    "attack": 190,
    "defence": 3.1,
    "HP": 2000,
    "recover_rate": 1,
    "spell_rate": 1,
    "buff_rate": 1,
    "crit_rate": 1.75,
    "life_steal_rate": 0,
    "dodge": 0.03,
    "skill_1": {
"""