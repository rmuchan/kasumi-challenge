import random
from typing import Dict, Any

import data
from rand import randomize


def create_skill(is_unique: bool) -> Dict[str, Any]:
    skill = randomize(data.numerical['skill_template'])
    effect = []
    if random.random() < data.numerical['single_effect_chance']:
        effect.append(_create_skill_effect(3, is_unique))
    else:
        effect.append(_create_skill_effect(2, is_unique))
        effect.append(_create_skill_effect(1, is_unique))
    skill['name'] = effect[0]['name']
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
    return effect


def get_skill_desc(skill: Dict[str, Any]) -> str:
    """生成技能描述。

    生成每个技能效果的描述，并加上技能名。

    :param skill: 技能
    :return: 插入具体数值的技能描述
    """
    return '【{name}】\n ├ 冷却回合：{cd}\n ├ MP消耗：{mp}\n └ 效果：{desc}'.format(
        name=skill['name'],
        cd=skill['cooldown'],
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
        return _BiasedRandomFormat(param)
    elif isinstance(param, int):
        return str(param)
    else:
        return _NumFormat(param)


class _BiasedRandomFormat:
    def __init__(self, val):
        self._val = _NumFormat(val[0])
        self._appraise = val[1]

    def __format__(self, format_spec: str):
        return format(self._val, format_spec) + f'({self._appraise})'


class _NumFormat:
    def __init__(self, val: float):
        self._val = val

    def __format__(self, format_spec: str):
        if format_spec and format_spec[-1] == '%':
            format_spec = format_spec[:-1]
            return format(self._val * 100, format_spec or '.0f') + '%'

        return format(self._val, format_spec or '.0f')
