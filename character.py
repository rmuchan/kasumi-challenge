import random
from typing import Dict, Any

import data
import rand
from interact import UI
from skill import get_skill_desc, create_skill


async def create_character(ui: UI):
    proto = ui.retrieve('proto_character')
    if isinstance(proto, dict) and proto.get('progress') == 'full':
        return _build_character_from_proto(proto)

    if not isinstance(proto, dict) or proto.get('progress') not in _CREATE_STEPS:
        proto = _init_proto_character(ui.uid())
        proto['progress'] = 'name'
        ui.store('proto_character', proto)

    ui.append('开始创建角色，当前进度：')
    await print_character(ui, proto)
    if proto['progress'] == next(iter(_CREATE_STEPS)):
        await ui.send(data.race[proto['race_id']]['desc'])

    while proto['progress'] in _CREATE_STEPS:
        handler, next_progress, should_print = _CREATE_STEPS[proto['progress']]
        await handler(ui, proto)
        proto['progress'] = next_progress
        ui.store('proto_character', proto)
        if should_print:
            await print_character(ui, proto)
    return _build_character_from_proto(proto)


def _init_proto_character(uid: int):
    template = data.numerical['character_template']
    proto = rand.randomize(template)
    race_id = uid % len(data.race)
    proto['race_id'] = race_id
    proto['race'] = data.race[race_id]['name']
    return proto


async def _create_step_name(ui: UI, proto: Dict[str, Any]):
    proto['name'] = await ui.input('给你的角色起个名字吧')


async def _create_step_skill_candidate(_: UI, proto: Dict[str, Any]):
    proto['skill_1_candidate'] = [create_skill(False) for _ in range(3)]
    proto['skill_2_candidate'] = [create_skill(False) for _ in range(3)]
    proto['skill_3_candidate'] = [create_skill(False) for _ in range(3)]
    proto['unique_candidate'] = [create_skill(True) for _ in range(3)]
    proto['passive_candidate'] = random.sample(data.skill_pool.passive, 3)


async def _create_step_passive_select(ui: UI, proto: Dict[str, Any]):
    candidate = proto['passive_candidate']
    ui.append('被动加成在下列项目中选择：')
    for idx, val in enumerate(candidate):
        ui.append('%d. %s' % (idx + 1, val['desc']))
    await ui.send()
    selection = await ui.input('选择被动加成')
    while not selection.isdigit() or int(selection) - 1 not in range(len(candidate)):
        selection = await ui.input('你的输入不正确，请重新输入')
    selection = int(selection) - 1
    proto['passive'] = candidate[selection]


def _create_step_skill_select(skill_num: int):
    async def skill_select(ui: UI, proto: Dict[str, Any]):
        candidate = proto[f'skill_{skill_num}_candidate']
        ui.append(f'第{skill_num}个技能在下列项目中选择：')
        for idx, val in enumerate(candidate):
            ui.append('%d. %s' % (idx + 1, get_skill_desc(val)))
        await ui.send()
        selection = await ui.input(f'选择第{skill_num}个技能')
        while not selection.isdigit() or int(selection) - 1 not in range(len(candidate)):
            selection = await ui.input('你的输入不正确，请重新输入')
        selection = int(selection) - 1
        proto[f'skill_{skill_num}'] = candidate[selection]

    return skill_select


async def _create_step_unique_select(ui: UI, proto: Dict[str, Any]):
    candidate = proto['unique_candidate']
    ui.append('终极技能在下列项目中选择：')
    for idx, val in enumerate(candidate):
        ui.append('%d. %s' % (idx + 1, get_skill_desc(val)))
    await ui.send()
    selection = await ui.input('选择终极技能')
    while not selection.isdigit() or int(selection) - 1 not in range(len(candidate)):
        selection = await ui.input('你的输入不正确，请重新输入')
    selection = int(selection) - 1
    proto['unique'] = candidate[selection]


async def _create_step_main_skill(ui: UI, proto: Dict[str, Any]):
    ui.append('你的技能有：')
    for idx in range(1, 4):
        ui.append('%d. %s' % (idx, get_skill_desc(proto[f'skill_{idx}'])))
    await ui.send()
    selection = await ui.input('选择主技能')
    while not selection.isdigit() or int(selection) - 1 not in range(3):
        selection = await ui.input('你的输入不正确，请重新输入')
    selection = int(selection)
    proto['skill_1'], proto[f'skill_{selection}'] = proto[f'skill_{selection}'], proto['skill_1']


_CREATE_STEPS = {
    'name': (_create_step_name, 'skill_candidate', False),
    'skill_candidate': (_create_step_skill_candidate, 'passive', True),
    'passive': (_create_step_passive_select, 'skill_1', False),
    'skill_1': (_create_step_skill_select(1), 'skill_2', False),
    'skill_2': (_create_step_skill_select(2), 'skill_3', False),
    'skill_3': (_create_step_skill_select(3), 'unique', False),
    'unique': (_create_step_unique_select, 'main_skill', False),
    'main_skill': (_create_step_main_skill, 'full', False),
}


def _build_character_from_proto(proto: Dict[str, Any]) -> Dict[str, Any]:
    assert proto['progress'] == 'full'
    fields_to_copy = [
        'name', 'race', 'race_id', 'lvl',
        'str_build', 'int_build', 'per_build', 'life_build', 'def_base',
        'defense_str_rate', 'magic_int_rate', 'health_per_rate', 'attack_rate',
        'passive', 'skill_1', 'skill_2', 'skill_3', 'unique',
    ]
    char = {k: proto[k] for k in fields_to_copy}
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
        'life': '生命'
    }
    for k, v in translate.items():
        ui.append('%s: %.0f + %.2f (%s)' % (v,
                                            data.numerical[f'{k}_base'] * char[f'{k}_build'][0],
                                            data.numerical[f'{k}_grow'] * char[f'{k}_build'][0],
                                            char[f'{k}_build'][1]))
    ui.append('基础物防: %.2f (%s)' % (char['def_base'][0], char['def_base'][1]))
    ui.append('攻击倍率: %.2f (%s)' % (char['attack_rate'][0], char['attack_rate'][1]))


def _print_step_passive(ui: UI, char: Dict[str, Any]):
    ui.append(char['passive']['desc'])


def _print_step_skill(skill_num: int):
    def append_skill(ui: UI, char: Dict[str, Any]):
        skill = char[f'skill_{skill_num}']
        ui.append(f'技能{skill_num}: %s' % get_skill_desc(skill))

    return append_skill


def _print_step_unique(ui: UI, char: Dict[str, Any]):
    ui.append('终极技能：%s' % get_skill_desc(char['unique']))


_PRINT_STEPS = {
    'name': _print_step_name,
    'passive': _print_step_passive,
    'skill_1': _print_step_skill(1),
    'skill_2': _print_step_skill(2),
    'skill_3': _print_step_skill(3),
    'unique': _print_step_unique,
}
