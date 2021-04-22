from . import util
from .character import calc_passive
from .data import data

numerical = data.numerical


# 生成每级升级需要的EXP
def _exp_requirement(lv: int) -> 100:
    return int(
        util.recurrence(numerical['exp_base'], numerical['exp_add_rate'], numerical['exp_add_point'], lv) / 100) * 100


# 生成经验数组
def _exp_overlay_gen() -> list:
    exp_overlay = [0]
    for i in range(1, 31):
        exp_overlay.append(exp_overlay[-1] + _exp_requirement(i))
    return exp_overlay


exp_overlay_list = _exp_overlay_gen()


def game_char_gen(chara: dict, test_lv=False, real_mode=True) -> dict:
    game_char = {}
    if test_lv:
        lv = test_lv
    else:
        lv = lv_calc(chara['exp'])

    if not real_mode:
        lv = numerical['fair_mode']

    str_ = attr_calc(numerical['str_base'] * chara['str_build'][0] + calc_passive(0, chara, 'str_base'),
                     numerical['str_grow'] * ((1 - chara['str_build'][0]) * numerical['attr_grow_expend'] + 1) + calc_passive(0, chara, 'str_grow'),
                     lv)
    int_ = attr_calc(numerical['int_base'] * chara['int_build'][0] + calc_passive(0, chara, 'int_base'),
                     numerical['int_grow'] * ((1 - chara['int_build'][0]) * numerical['attr_grow_expend'] + 1) + calc_passive(0, chara, 'int_grow'),
                     lv)
    per_ = attr_calc(numerical['per_base'] * chara['per_build'][0] + calc_passive(0, chara, 'per_base'),
                     numerical['per_grow'] * ((1 - chara['per_build'][0]) * numerical['attr_grow_expend'] + 1) + calc_passive(0, chara, 'per_grow'),
                     lv)

    game_char['str'] = str_
    game_char['int'] = int_
    game_char['per'] = per_

    game_char['name'] = chara['name']
    game_char['not_short_hp'] = True
    game_char['attack'] = _atk_calc(str_, int_, chara['defense_str_rate'], chara['attack_rate'][0])
    game_char['defence'] = _def_calc(per_, calc_passive(chara['def_base'][0], chara, 'def_base'))
    game_char['HP'] = hp_calc(str_,
                              numerical['life_base'] * chara['life_build'][0] + calc_passive(0, chara, 'life_base'),
                              numerical['life_grow'] * chara['life_build'][0] + calc_passive(0, chara, 'life_grow'),
                              lv,
                              calc_passive(numerical['hp_rate'], chara, 'hp_rate'))

    game_char['base_skill_chance_boost'] = calc_passive(numerical['base_skill_chance_boost'], chara, 'skill_chance_boost')
    game_char['mp_consume_dec'] = calc_passive(1, chara, 'mp_consume_dec')

    # 三倍率为玩家基础属性计算得来的倍率 乘以被动带来的增益
    game_char['recover_rate'] = _recover_rate_calc(per_, str_, chara['health_per_rate']) * calc_passive(1.0, chara, 'recover_rate')
    game_char['spell_rate'] = _spell_rate_calc(int_, per_, chara['magic_int_rate']) * calc_passive(1.0, chara, 'spell_rate')
    game_char['buff_rate'] = _buff_rate_calc(per_) * calc_passive(1.0, chara, 'buff_rate')

    game_char['std_rate'] = attr_based_enhance(attr_calc(numerical['std_attr'], numerical['std_attr_grow'], lv))

    game_char['crit_rate'] = str_ * numerical['crit_int_convert_rate'] + chara['base_crit_rate'][0] + calc_passive(0, chara, 'crit_rate')
    game_char['crit_chance'] = numerical['crit_chance']
    game_char['life_steal_rate'] = calc_passive(numerical['life_steal_rate_base'], chara, 'life_steal_rate')
    game_char['dodge'] = _dodge_calc(int_, calc_passive(0, chara, 'dodge'))

    game_char['skills'] = [chara[f'skill_{i}'] for i in range(1, 4)]
    game_char['unique'] = chara['unique'].copy()

    game_char['lv'] = lv

    game_char['normal_attack'] = {
        'name': '普通攻击',
        'effect': [
            {
                'type': 'NORMAL_ATK',
                'target': {
                    'type': "RAND",
                    'team': 0,
                    'limit': 1
                },
                'param': []
            }
        ]
    }

    game_char['tag'] = {}


    # 特殊效果处理
    for effect in chara['unique']["effect"]:
        if effect.get('passive'):
            # 普攻特效
            temp = effect.copy()
            if effect['passive_type'] == 'normal_attack_enhance':
                game_char['normal_attack']['effect'] += [temp]
            # 添加标签
            elif effect['passive_type'] == 'add_tag':
                for k, v in temp['tag'].items():
                    game_char['tag'][k] = v
            # 蓝耗变化
            elif effect['passive_type'] == 'mp_consume_change':
                game_char['mp_consume_dec'] *= effect['param'][0]
                if len(effect['param']) > 1:
                    for sk in game_char['skills']:
                        sk['mp_cost'] += effect['param'][1]

            del temp['passive']


    # print(game_char)
    return game_char


# 属性计算
def attr_calc(attr_base, attr_grow, lv):
    return util.recurrence(attr_base, numerical['attr_rate'], attr_grow, lv)


# 攻击计算
def _atk_calc(str_cur, int_cur, defense_str_rate, atk_rate):
    adj = str_cur * defense_str_rate + int_cur * (1 - defense_str_rate)
    return (adj * atk_rate / numerical['atk_avr']) ** numerical['atk_index'] * numerical['atk_avr']


# 血量计算  -  modify基本上就是给Shadoul用的了(
def hp_calc(str_cur, life_base, life_grow, lv, modify):
    return (util.recurrence(str_cur, numerical['hp_lv_rate'], life_grow, lv) + life_base) * modify


# 防御计算
def _def_calc(per_cur, def_base):
    return per_cur * numerical['def_adj_rate'] + def_base


# 下面会有三个基于属性的技能强化率的计算会用到这个函数
def attr_based_enhance(attr):
    return numerical['enhance_constant'] * (attr ** numerical['enhance_exponent'])


# 护盾与治疗倍率
def _recover_rate_calc(per_cur, str_cur, health_per_rate):
    return attr_based_enhance(per_cur * health_per_rate + str_cur * (1 - health_per_rate))


# 魔法伤害增强 - 对于Magecian种族，mage_rate会有更高的数值
def _spell_rate_calc(int_cur, per_cur, magic_int_rate):
    return attr_based_enhance(int_cur * magic_int_rate + per_cur * (1 - magic_int_rate))


# 增益类技能效果增强
def _buff_rate_calc(per_cur):
    return attr_based_enhance(per_cur)


# 闪避
def _dodge_calc(int_cur, extra):
    return numerical['dodge_base'] + extra + int_cur * numerical['dodge_rate']


# 根据经验等级计算
def lv_calc(exp: int):
    for i in range(1, 30):
        if exp_overlay_list[i - 1] <= exp < exp_overlay_list[i]:
            return i
    return 30
