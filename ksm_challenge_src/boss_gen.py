#from .rand import randomize
#from .data import data
import json

from ksm_challenge_src.GameChar import numerical
from ksm_challenge_src.rand import randomize


def recurrence(a_1: float, k: float, m: float, n: int) -> float:
    return (a_1 - m) * k ** (n - 1) + m * (k ** n - 1) / (k - 1)


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
    print(rating)
    return boss


def attack_calc(atk, lv):
    return recurrence(atk, numerical['attr_rate'] ,atk*0.02, lv)


def hp_calc(hp_base, life_base, lv):
    add = recurrence(life_base, numerical['attr_rate'], life_base * 0.02, lv)
    return (recurrence(add, numerical['attr_rate'], add * 0.0225, lv) + hp_base) * numerical['hp_rate']


def rates_3_calc(lv):
    virtual_attr = recurrence(numerical['per_base'] * 1.16, numerical['attr_rate'], numerical['per_grow'], lv)
    return numerical['enhance_constant'] * (virtual_attr ** numerical['enhance_exponent'])


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