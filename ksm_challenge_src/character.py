import random
from typing import Dict, Any

from . import rand
from .GameChar import numerical
from .data import data
from .interact import UI
from .skill import get_skill_desc, create_skill, create_unique_skill
from .talent_calc import build_talent_buff
from .user_guide import get_ver


async def create_character(ui: UI):
    proto = ui.retrieve('proto_character')
    if isinstance(proto, dict) and proto.get('progress') == 'full':
        return _build_character_from_proto(ui, proto)

    if not isinstance(proto, dict) or proto.get('progress') not in _CREATE_STEPS:
        proto = _init_proto_character(ui.uid())
        proto['talent'] = build_talent_buff(ui)
        proto['progress'] = 'name'
        ui.store('proto_character', proto)

    ui.append('开始创建角色，当前进度：')
    await print_character(ui, proto)
    if not ui.retrieve('created') and proto['progress'] == next(iter(_CREATE_STEPS)):
        await ui.send(data.race[proto['race_id']]['desc'])

    while proto['progress'] in _CREATE_STEPS:
        handler, next_progress, should_print = _CREATE_STEPS[proto['progress']]
        await handler(ui, proto)
        proto['progress'] = next_progress
        ui.store('proto_character', proto)
        if should_print:
            await print_character(ui, proto)
    return _build_character_from_proto(ui, proto)


def _init_proto_character(uid: int):
    template = data.numerical['character_template']
    proto = rand.randomize(template)
    race_id = uid % len(data.race)
    proto['race_id'] = race_id
    proto['race'] = data.race[race_id]['name']
    proto['game_version'] = get_ver()
    return proto


async def _create_step_name(ui: UI, proto: Dict[str, Any]):
    proto['name'] = await ui.input('↓ 请为你的角色命名(12个英文字符/6个汉字以内，过长的名字将会被忽略)：',
                                   is_valid=lambda x: len(x) + sum(1 for y in x if ord(y) > 127) <= 12)


async def _create_step_skill_candidate(_: UI, proto: Dict[str, Any]):
    proto['skill_1_candidate'] = [create_skill() for _ in range(3)]
    proto['skill_2_candidate'] = [create_skill() for _ in range(3)]
    proto['skill_3_candidate'] = [create_skill() for _ in range(3)]
    proto['unique_candidate'] = create_unique_skill(3)
    proto['passive_candidate'] = random.sample(data.skill_effect_pool.passive, 3)


async def _create_step_passive_select(ui: UI, proto: Dict[str, Any]):
    candidate = proto['passive_candidate']
    ui.append('被动加成在下列项目中选择：')
    for idx, val in enumerate(candidate):
        ui.append('[%d] %s' % (idx + 1, val['desc']))
    ui.append('—' * 12)
    await ui.send(' ↓ 选择被动加成（输入选项序号）：')

    selection = await ui.input(is_valid=lambda x: x.isdigit() and int(x) - 1 in range(len(candidate)))
    selection = int(selection) - 1
    proto['passive'] = candidate[selection]


def _create_step_skill_select(skill_num: int):
    async def skill_select(ui: UI, proto: Dict[str, Any]):
        candidate = proto[f'skill_{skill_num}_candidate']
        ui.append(f'第{skill_num}个技能在下列项目中选择：')
        for idx, val in enumerate(candidate):
            ui.append('[%d] %s' % (idx + 1, get_skill_desc(val, False)))
        ui.append('—' * 12)
        await ui.send(f' ↓ 选择第{skill_num}个技能（输入选项序号）：')
        selection = await ui.input(is_valid=lambda x: x.isdigit() and int(x) - 1 in range(len(candidate)))
        selection = int(selection) - 1
        proto[f'skill_{skill_num}'] = candidate[selection]

    return skill_select


async def _create_step_unique_select(ui: UI, proto: Dict[str, Any]):
    candidate = proto['unique_candidate']
    ui.append('终极技能在下列项目中选择：')
    for idx, val in enumerate(candidate):
        ui.append('[%d] %s' % (idx + 1, get_skill_desc(val, True)))
    ui.append('—' * 12)
    await ui.send(' ↓ 选择终极技能（输入选项序号）：')
    selection = await ui.input(is_valid=lambda x: x.isdigit() and int(x) - 1 in range(len(candidate)))
    selection = int(selection) - 1
    proto['unique'] = candidate[selection]


async def _create_step_main_skill(ui: UI, proto: Dict[str, Any]):
    ui.append('你的技能有：')
    for idx in range(1, 4):
        ui.append('[%d] %s' % (idx, get_skill_desc(proto[f'skill_{idx}'], False)))
    ui.append('—' * 12)
    ui.append('主技能会提升发动概率，减少冷却时间，并降低MP消耗')
    await ui.send(' ↓ 选择主技能（输入选项序号）：')
    selection = await ui.input(is_valid=lambda x: x.isdigit() and int(x) - 1 in range(3))
    selection = int(selection)
    primary = proto[f'skill_{selection}']
    proto['skill_1'], proto[f'skill_{selection}'] = primary, proto['skill_1']
    primary['chance'] *= data.numerical['primary_skill_chance_rate']
    primary['cooldown'] = int(primary['cooldown'] * data.numerical['primary_skill_cooldown_rate'])
    primary['mp_cost'] *= data.numerical['primary_skill_cost_decrease']


_CREATE_STEPS = {
    'name': (_create_step_name, 'skill_candidate', False),
    'skill_candidate': (_create_step_skill_candidate, 'unique', True),
    'unique': (_create_step_unique_select, 'skill_1', False),
    'skill_1': (_create_step_skill_select(1), 'skill_2', False),
    'skill_2': (_create_step_skill_select(2), 'skill_3', False),
    'skill_3': (_create_step_skill_select(3), 'main_skill', False),
    'main_skill': (_create_step_main_skill, 'passive', False),
    'passive': (_create_step_passive_select, 'full', False),
}


def _build_character_from_proto(ui: UI, proto: Dict[str, Any]) -> Dict[str, Any]:
    assert proto['progress'] == 'full'
    fields_to_copy = [
        'name', 'race', 'race_id', 'game_version', 'talent', 'exp',
        'str_build', 'int_build', 'per_build', 'life_build', 'def_base',
        'defense_str_rate', 'magic_int_rate', 'health_per_rate', 'attack_rate', 'base_crit_rate',
        'passive', 'skill_1', 'skill_2', 'skill_3', 'unique',
    ]
    char = {k: proto[k] for k in fields_to_copy}
    ui.store('character', char)
    ui.store('proto_character', None)
    ui.store('created', True)
    return char


async def print_character(ui: UI, char: Dict[str, Any]):
    progress = char.get('progress')
    brand_new = True
    for step in _CREATE_STEPS:
        if progress == step:
            break
        brand_new = False
        _PRINT_STEPS.get(step, lambda *_: None)(ui, char)
    if brand_new:
        ui.append('崭新的%s' % char['race'])
    await ui.send()


def _print_step_name(ui: UI, char: Dict[str, Any]):
    ui.append('%s·%s' % (char['name'], char['race']))
    translate = {
        'str': '力量',
        'int': '敏捷',
        'per': '感知',
    }
    for k, v in translate.items():
        ui.append('%s: %.0f + %.2f (%s)' %
                  (v,
                   calc_passive(data.numerical[f'{k}_base'] * char[f'{k}_build'][0], char, f'{k}_base'),
                   calc_passive(data.numerical[f'{k}_grow'] * ((1 - char[f'{k}_build'][0]) * numerical['attr_grow_expend'] + 1), char, f'{k}_grow'),
                   char[f'{k}_build'][1]))
    from .attr_calc import hp_calc
    ui.append('生命: %.0f + %.1f (%s)' % (
        hp_calc(calc_passive(data.numerical['str_base'] * char['str_build'][0], char, 'str_base'),
                calc_passive((char['life_build'][0] * data.numerical['life_base']), char, 'hp_base'),
                data.numerical['life_grow'] * char['life_build'][0], 1,
                calc_passive(data.numerical['hp_rate'], char, 'hp_rate')),
        calc_passive(data.numerical['life_grow'] * char['life_build'][0], char, 'life_grow') * data.numerical['hp_rate'],
        char['life_build'][1]
    )
              )
    ui.append('基础物防: %.2f (%s)' % (calc_passive(char['def_base'][0], char, 'def_base'), char['def_base'][1]))
    ui.append('攻击倍率: {:.0%} ({})'.format(char['attack_rate'][0], char['attack_rate'][1]))
    ui.append('基础暴击倍率: {:.0%} ({})'.format(calc_passive(char['base_crit_rate'][0], char, 'base_crit_rate'),
                                           char['base_crit_rate'][1]))
    ui.append('(如果您不清楚这些属性的意义，您可以使用像\n"ksmgame-help 力量"\n这样的指令查询每个属性的意义)')


def _print_step_passive(ui: UI, char: Dict[str, Any]):
    ui.append('被动加成: %s' % char['passive']['desc'])


def _print_step_skill(skill_num: int):
    def append_skill(ui: UI, char: Dict[str, Any]):
        skill = char[f'skill_{skill_num}']
        ui.append(f'技能{skill_num}: %s' % get_skill_desc(skill, False))

    return append_skill


def _print_step_unique(ui: UI, char: Dict[str, Any]):
    ui.append('终极技能：%s' % get_skill_desc(char['unique'], True))


_PRINT_STEPS = {
    'name': _print_step_name,
    'passive': _print_step_passive,
    'skill_1': _print_step_skill(1),
    'skill_2': _print_step_skill(2),
    'skill_3': _print_step_skill(3),
    'unique': _print_step_unique,
}


def calc_passive(base: float, char: dict, key: str) -> float:
    race = data.race[char['race_id']]['buff']
    passive = char.get('passive', {}).get('buff', {})
    talent = char.get('talent', {})
    add = 0
    madd = 0
    multiply = 1
    for b in (race, passive, talent):
        modify = b.get(key, 0)
        if not isinstance(modify, dict):
            add += modify
        elif 'madd' in modify:
            madd += modify['madd']
        else:
            multiply *= modify['multiply']
    return (base + add) * (1 + madd) * multiply


def exp_to_talent_coin(exp):
    return int(exp ** data.numerical['talent_coin_earn_index'] * data.numerical['talent_coin_earn_rate'])
