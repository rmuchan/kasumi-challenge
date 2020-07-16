import data

numerical = data.numerical


def game_char_gen(chara: dict) -> dict:
    game_char = {}
    str_ = _attr_calc(numerical['str_base'] * chara['str_build'][0],
                      numerical['str_grow'] * chara['str_build'][0],
                      chara['lvl'])
    int_ = _attr_calc(numerical['int_base'] * chara['int_build'][0],
                      numerical['int_grow'] * chara['int_build'][0],
                      chara['lvl'])
    per_ = _attr_calc(numerical['per_base'] * chara['per_build'][0],
                      numerical['per_grow'] * chara['per_build'][0],
                      chara['lvl'])

    game_char['name'] = chara['name']
    game_char['attack'] = _atk_calc(int_)
    game_char['defence'] = _def_calc(str_, int_, chara['defense_str_rate'],
                                     _calc_passive(chara['def_base'][0], chara, 'def_base'), )
    game_char['HP'] = _hp_calc(str_,
                               numerical['life_base'] * chara['life_build'][0],
                               numerical['life_grow'] * chara['life_build'][0],
                               chara['lvl'],
                               _calc_passive(numerical['hp_rate'], chara, 'hp_rate'))
    game_char['recover_rate'] = _recover_rate_calc(per_, str_, chara['health_per_rate'])
    game_char['spell_rate'] = _spell_rate_calc(int_, per_, chara['magic_int_rate'],
                                               _calc_passive(1.0, chara, 'spell_rate'))
    game_char['buff_rate'] = _buff_rate_calc(per_)
    game_char['crit_rate'] = _calc_passive(numerical['crit_base'], chara, 'crit_rate')
    game_char['life_steal_rate'] = _calc_passive(0, chara, 'life_steal_rate')
    game_char['dodge'] = _dodge_calc(per_, _calc_passive(0, chara, 'dodge'))

    for i in range(1, 4):
        game_char[f'skill_{i}'] = chara[f'skill_{i}']

    game_char['unique'] = chara['unique']

    game_char['normal_attack'] = {
        'name': '普通攻击',
        'effect': {
            'type': 'NORMAL_ATK',
            'target': {
                'type': "RAND",
                'team': 0,
                'limit': 1
            }
        }
    }

    return game_char


# 属性计算
def _attr_calc(attr_base, attr_grow, lv):
    current = attr_base
    for _ in range(lv - 1):
        current = current * (numerical['attr_rate']) + attr_grow
    return current


# 攻击计算
def _atk_calc(int_cur):
    return int_cur * numerical['atk_rate']


# 血量计算  -  modify基本上就是给Shadoul用的了(
def _hp_calc(str_cur, life_base, life_grow, lv, modify):
    current = str_cur
    for _ in range(lv - 1):
        current = current * numerical['hp_lv_rate'] + life_grow
    hp = life_base + current
    hp *= modify
    return hp


# 防御计算
def _def_calc(str_cur, int_cur, defense_str_rate, def_base):
    adj = str_cur * defense_str_rate + int_cur * (1 - defense_str_rate)
    return adj * numerical['def_adj_rate'] + def_base


# 暴击率增益计算
def _crit_rate_calc(str_cur, int_cur, defense_str_rate, def_base):
    adj = str_cur * defense_str_rate + int_cur * (1 - defense_str_rate)
    return adj * numerical['def_adj_rate'] + def_base


# 下面会有三个基于属性的技能强化率的计算会用到这个函数
def _attr_based_enhance(attr):
    return numerical['enhance_constant'] * (attr ** numerical['enhance_exponent'])


# 护盾与治疗倍率
def _recover_rate_calc(per_cur, str_cur, health_per_rate):
    return _attr_based_enhance(per_cur * health_per_rate + str_cur * (1 - health_per_rate))


# 魔法伤害增强 - 对于Magecian种族，mage_rate会有更高的数值
def _spell_rate_calc(int_cur, per_cur, magic_int_rate, extra=1.0):
    return _attr_based_enhance(int_cur * magic_int_rate + per_cur * (1 - magic_int_rate)) * extra


# 增益类技能效果增强
def _buff_rate_calc(per_cur):
    return _attr_based_enhance(per_cur)


# 闪避
def _dodge_calc(per_cur, extra):
    return numerical['dodge_base'] + extra + per_cur * numerical['dodge_rate']


def _calc_passive(base: float, char: dict, key: str) -> float:
    race = data.race[char['race_id']]['buff']
    passive = char['passive']['buff']
    add = 0
    multiply = 1
    for b in (race, passive):
        modify = b.get(key, 0)
        if isinstance(modify, dict):
            multiply *= modify['multiply']
        else:
            add += modify
    return (base + add) * multiply
