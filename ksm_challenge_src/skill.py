import random
from typing import Dict, Any, Iterable

from . import util
from .data import data
from .rand import randomize


def create_skill(is_unique: bool) -> Dict[str, Any]:
    if is_unique or random.random() < data.numerical['single_effect_chance']:
        pool = data.skill_effect_pool['unique' if is_unique else 'lv-3']
        template = random.choices(pool, [x['weight'] for x in pool])[0]
        skill = randomize(template)
        for effect in skill['effect']:
            _process_effect(effect)
    else:
        skill = randomize(data.numerical['skill_template'])
        # noinspection PyListCreation
        effect = [_create_skill_effect(2, ())]
        effect.append(_create_skill_effect(1, effect[0]['type']))
        skill['name'] = '·'.join(x['name'] for x in effect)
        skill['effect'] = effect
    return skill


def _create_skill_effect(level: int, forbidden_type: Iterable[str]) -> Dict[str, Any]:
    pool = data.skill_effect_pool[f'lv-{level}']
    pool = list(filter(lambda x: x['type'] not in forbidden_type, pool))
    template = random.choices(pool, [x['weight'] for x in pool])[0]
    effect = randomize(template)
    _process_effect(effect)
    return effect


def _process_effect(effect: Dict[str, Any]):
    if effect['target']['type'] not in ('SELF', 'ALL', 'OTHER') and effect['param']:
        limit = effect['target']['limit']
        old = effect['param'][0]
        if isinstance(old, tuple):
            effect['param'][0] = (_calc_aoe_param(old[0], limit), old[1])
        else:
            effect['param'][0] = _calc_aoe_param(old, limit)


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
        return '【{name}】\n └ 效果：{desc}'.format(
            name=skill['name'],
            desc='；'.join(get_effect_desc(x) for x in skill['effect'])
        )
    else:
        return '【{name}】\n ├ 冷却回合：{cd}\n ├ 概率：{chance:.1%}\n ├ MP消耗：{mp}\n └ 效果：{desc}'.format(
            name=skill['name'],
            cd=skill['cooldown'],
            chance=real_chance_calc(skill['chance']),
            mp=skill['mp_cost'],
            desc='；'.join(get_effect_desc(x) for x in skill['effect'])
        )


def real_chance_calc(chance):
    last_time = 1
    Sum = 0
    sample_count = 1000
    for i in range(sample_count):
        if random.random() < chance * last_time:
            # 发动了
            last_time = 1
            Sum += 1
        else:
            last_time += 1
    return Sum / sample_count

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
