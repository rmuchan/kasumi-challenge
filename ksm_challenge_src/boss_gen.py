import json

from .attr_calc import attr_based_enhance, attr_calc
from .GameChar import numerical
from .rand import randomize
from .util import recurrence


def boss_gen(template: dict, lv):
    bosses = []
    total_weight = 0
    power_rating = 0
    for boss_template in template['bosses']:
        boss, rating = creature_gen(boss_template, lv)
        bosses.append(boss)
        weight = boss.get('weight', 1)
        total_weight += weight
        power_rating += ((rating[0] * 2 / rating[1] - 1) * 0.4 + 1) * weight
    power_rating /= total_weight
    bosses[0]['exp_earn'] = int(power_rating * exp_earn_calc(lv))
    final_rating = recurrence(numerical['per_base'], numerical['attr_rate'], numerical['per_grow'], lv) ** 1.4 * power_rating
    return {
        'desc': template['desc'],
        'bosses': bosses,
        'final_rating': final_rating
    }


def creature_gen(template: dict, lv):
    rating = [0, 0]
    creature = randomize(template, rating)
    creature['attack'] = attack_calc(creature['attack'], lv)
    creature['defence'] = creature['defence_base'] + lv * creature['defence_grow']
    del creature['defence_base'], creature['defence_grow']
    creature['HP'] = hp_calc(creature['hp_base'], creature['life_base'], lv)
    del creature['hp_base'], creature['life_base']
    creature['recover_rate'] *= rates_3_calc(lv)
    creature['spell_rate'] *= rates_3_calc(lv)
    creature['buff_rate'] *= rates_3_calc(lv)
    creature['std_rate'] = attr_based_enhance(attr_calc(numerical['std_attr'], numerical['std_attr_grow'], lv))
    creature['is_boss'] = True
    creature['exp_earn'] = 0
    creature['lv'] = lv
    creature['base_skill_chance_boost'] = creature.get('base_skill_chance_boost', 1)
    return creature, rating


def attack_calc(atk, lv):
    return recurrence(atk, numerical['attr_rate'], atk*0.022, lv)


def hp_calc(hp_base, life_base, lv):
    add = recurrence(life_base, numerical['attr_rate'], life_base * 0.02, lv)
    return (recurrence(add, numerical['attr_rate'], add * 0.021, lv) + hp_base) * numerical['hp_rate']


def rates_3_calc(lv):
    virtual_attr = recurrence(numerical['boss_virtual_attr'], numerical['attr_rate'], numerical['per_grow'], lv)
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
    for i in [1, 10, 20, 30]:
        print(boss_gen(boss_json, i))
