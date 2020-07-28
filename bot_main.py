import asyncio
import random

from nonebot import CommandSession, CommandGroup
from nonebot.session import BaseSession

from .ksm_challenge_src.Gaming import Gaming
from .ksm_challenge_src.attr_calc import game_char_gen, lv_calc
from .ksm_challenge_src.boss_gen import boss_gen
from .ksm_challenge_src.bot_ui import BotContextUI
from .ksm_challenge_src.character import create_character, print_character, exp_to_talent_coin
from .ksm_challenge_src.data import data
from .ksm_challenge_src.interact import UI
from .ksm_challenge_src.talent_calc import upgrade_talent

_battles = {}
_cmd_group = CommandGroup('ksmgame', only_to_me=False)


# 新建
@_cmd_group.command('create')
async def _(session: CommandSession):
    async def create(ui: UI):
        if ui.retrieve('character') is not None:
            await ui.send('你已经有角色了（')
            await print_character(ui, ui.retrieve('character'))
            return
        char = await create_character(ui)
        ui.store('character', char)
        ui.store('proto_character', None)
        await print_character(ui, char)

    try:
        BotContextUI(session.bot, session.ctx).run(create, mutex_mode='user')
    except BotContextUI.RunningException:
        await session.send(session.bot.config.SESSION_RUNNING_EXPRESSION)


# 查询角色信息
@_cmd_group.command('query')
async def _(session: CommandSession):
    ui = BotContextUI(session.bot, session.ctx)
    char = ui.retrieve('character')
    if char is None:
        return await ui.send('你还没有创建角色')
    await print_character(ui, char)


# 发起pve
@_cmd_group.command('pve')
async def _(session: CommandSession):
    ui = BotContextUI(session.bot, session.ctx)
    if session.ctx['message_type'] != 'group':
        return await ui.send('只能在群里用（')
    group_id = session.ctx['group_id']
    if group_id in _battles:
        return await ui.send('正打着呢（')
    char = ui.retrieve('character')
    if char is None:
        return await ui.send('建角色，请（')

    boss, is_saved = _get_boss(group_id, lv_calc(char['exp']))
    if is_saved:
        ui.append('上次没人打的boss又回来辣（')
    await ui.send(boss['desc'])

    _battles[group_id] = {
        'can_join': True,
        'is_pvp': False,
        'team_a': {},
        'team_b': {0: boss},
        'capacity_a': 4,
        'capacity_b': 1
    }
    _battles[group_id]['team_a'][ui.uid()] = game_char_gen(char)
    await ui.send('你发起并加入了一场boss战（')

    asyncio.ensure_future(_remove_battle(session))


# 发起pvp
@_cmd_group.command('pvp')
async def _(session: CommandSession):
    ui = BotContextUI(session.bot, session.ctx)
    if session.ctx['message_type'] != 'group':
        return await ui.send('只能在群里用（')
    group_id = session.ctx['group_id']
    if group_id in _battles:
        return await ui.send('正打着呢（')
    char = ui.retrieve('character')
    if char is None:
        return await ui.send('建角色，请（')

    _battles[group_id] = {
        'can_join': True,
        'is_pvp': True,
        'team_a': {},
        'team_b': {},
        'capacity_a': 4,
        'capacity_b': 4
    }
    _battles[group_id]['team_a'][ui.uid()] = game_char_gen(char)
    await ui.send('你发起了一场决斗，并加入了a队（')

    asyncio.ensure_future(_remove_battle(session))


# 加入战斗
@_cmd_group.command('join')
async def _(session: CommandSession):
    ui = BotContextUI(session.bot, session.ctx)
    if session.ctx['message_type'] != 'group':
        return await ui.send('只能在群里用（')
    group_id = session.ctx['group_id']
    if group_id not in _battles:
        return await ui.send('现在没有战斗（')
    bat = _battles[group_id]
    if not bat['can_join']:
        return await ui.send('已经开打了（')

    if ui.uid() in bat['team_a'] or ui.uid() in bat['team_b']:
        return await ui.send('你已经加入当前战斗了（')

    team = session.current_arg.lower()
    if bat['is_pvp']:
        if team not in ('a', 'b'):
            return await ui.send('只有a和b队（')
    else:
        if team not in ('', 'a'):
            return await ui.send('只能加入a队（')
        team = 'a'

    if len(bat[f'team_{team}']) >= bat[f'capacity_{team}']:
        return await ui.send('队伍满了（')

    char = ui.retrieve('character')
    if char is None:
        return await ui.send('建角色，请（')
    bat[f'team_{team}'][ui.uid()] = game_char_gen(char)
    if len(bat['team_a']) < bat['capacity_a'] or len(bat['team_b']) < bat['capacity_b']:
        return await ui.send(f'你加入了{team}队')

    bat['can_join'] = False
    await ui.send('人齐了，开打！')

    async def play(ui_: UI):
        if not bat['is_pvp']:
            save = data.saves.group[str(group_id)] or {}
            if save.pop('boss', None) is not None:
                data.saves.group[str(group_id)] = save
        
        game = Gaming(bat['team_a'].values(), bat['team_b'].values(), ui_)
        result = await game.start()
        await ui_.send(result)
        del _battles[group_id]

    try:
        ui.run(play, mutex_mode='group')
    except BotContextUI.RunningException:
        await session.send(session.bot.config.SESSION_RUNNING_EXPRESSION)


# 转生
@_cmd_group.command('rebirth')
async def _(session: CommandSession):
    ui = BotContextUI(session.bot, session.ctx)
    char = ui.retrieve('character')
    if char is None:
        return await ui.send('您转生啥着呢（')
    coin = ui.retrieve('talent_coin') or 0
    acquire_coin = exp_to_talent_coin(char['exp'])
    ui.store('talent_coin', coin + acquire_coin)
    ui.store('character', None)
    await ui.send(f'你的角色化为了{acquire_coin}个天赋币')


# 天赋管理
@_cmd_group.command('talent')
async def _(session: CommandSession):
    try:
        BotContextUI(session.bot, session.ctx).run(upgrade_talent, mutex_mode='user')
    except BotContextUI.RunningException:
        await session.send(session.bot.config.SESSION_RUNNING_EXPRESSION)


def _get_boss(gid: int, lvl: int):
    save = data.saves.group[str(gid)] or {}
    boss = save.get('boss')
    if boss is not None:
        return boss, True

    pool = data.boss_pool
    template = pool[random.choice(pool.dir())]
    boss = boss_gen(template, lvl)
    save['boss'] = boss
    data.saves.group[str(gid)] = save
    return boss, False


async def _remove_battle(session: BaseSession):
    group_id = session.ctx['group_id']
    await asyncio.sleep(60)
    if group_id in _battles and _battles[group_id]['can_join']:
        del _battles[group_id]
        await session.send('凑不齐人，摸了（')
