import random
from typing import Dict, Any

from . import util
from .data import data
from .rand import randomize


def create_skill(is_unique: bool) -> Dict[str, Any]:
    skill = randomize(data.numerical['skill_template'])
    effect = []
    if random.random() < data.numerical['single_effect_chance']:
        effect.append(_create_skill_effect(3, is_unique))
    else:
        effect.append(_create_skill_effect(2, is_unique))
        effect.append(_create_skill_effect(1, is_unique))
    skill['name'] = '·'.join(x['name'] for x in effect)
    skill['effect'] = effect
    return skill


def _create_skill_effect(level: int, is_unique: bool) -> Dict[str, Any]:
    pool = data.skill_effect_pool[f'lv-{level}']
    template = random.choices(pool, [x['weight'] for x in pool])[0]
    effect = randomize(template)
    if 'param' not in effect:
        effect['param'] = effect['unique_param' if is_unique else 'skill_param']
        del effect['skill_param']
        del effect['unique_param']
    if effect['target']['type'] not in ('SELF', 'ALL', 'OTHER'):
        limit = effect['target']['limit']
        old = effect['param'][0]
        if isinstance(old, tuple):
            effect['param'][0] = (_calc_aoe_param(old[0], limit), old[1])
        else:
            effect['param'][0] = _calc_aoe_param(old, limit)
    return effect


def _calc_aoe_param(base: float, limit: int) -> float:
    rate = data.numerical['aoe_separate_rate']
    return base * (rate[limit] if limit < len(rate) else rate[-1])


def get_skill_desc(skill: Dict[str, Any], is_unique: bool) -> str:
    """生成技能描述。

    生成每个技能效果的描述，并加上技能名。

    :param skill: 技能
    :param is_unique: 是否为终极技能
    :return: 插入具体数值的技能描述
    """
    if is_unique:
        format_ = '【{name}】\n └ 效果：{desc}'
    else:
        format_ = '【{name}】\n ├ 冷却回合：{cd}\n ├ 动态概率：{chance:.1f%}\n ├ MP消耗：{mp}\n └ 效果：{desc}'
    return format_.format(
        name=skill['name'],
        cd=skill['cooldown'],
        chance=util.NumFormat(skill['chance']),
        mp=skill['mp_cost'],
        desc='；'.join(get_effect_desc(x) for x in skill['effect'])
    )


def get_effect_desc(effect: Dict[str, Any]) -> str:
    """生成技能效果描述。

    以技能效果desc字段为模板，传入参数。模板中可以插入用于str.format的格式化字符串，format时会将effect展开作为命名参数传入。
    param元素如果由biased随机函数生成，则会以8.00(SS)的形式同时插入其数值和评级，否则只插入其数值（保留两位小数）。
    除param外的元素原样传入。

    :param effect: 技能效果
    :return: 插入具体数值的效果描述
    """
    return effect['desc'].format(param=[_get_param_desc(x) for x in effect['param']],
                                 **{k: v for k, v in effect.items() if k != 'param'})


def _get_param_desc(param):
    if isinstance(param, (list, tuple)):
        return util.BiasedRandomFormat(param)
    elif isinstance(param, int):
        return str(param)
    else:
        return util.NumFormat(param)
