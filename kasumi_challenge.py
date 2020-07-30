import asyncio
import random
import time

from nonebot import CommandSession, CommandGroup
from nonebot.session import BaseSession

from .ksm_challenge_src.user_guide import show_help, show_guide
from .ksm_challenge_src.Gaming import Gaming
from .ksm_challenge_src.attr_calc import game_char_gen, lv_calc
from .ksm_challenge_src.boss_gen import boss_gen
from .ksm_challenge_src.bot_ui import BotContextUI
from .ksm_challenge_src.character import create_character, print_character, exp_to_talent_coin, calc_passive
from .ksm_challenge_src.character_show import show_chara_info
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
            await ui.send('你已经拥有了一个角色！你可以使用ksmgame-status来查看属性')
            return
        char = await create_character(ui)
        ui.store('character', char)
        ui.store('proto_character', None)
        ui.append('角色创建完成！')
        await print_character(ui, char)

    try:
        BotContextUI(session.bot, session.ctx).run(create, mutex_mode='user')
    except BotContextUI.RunningException:
        await session.send(session.bot.config.SESSION_RUNNING_EXPRESSION)


# 查询角色信息
@_cmd_group.command('status')
async def _query(session: CommandSession):
    ui = BotContextUI(session.bot, session.ctx)
    await show_chara_info(ui)


@_cmd_group.command('help')
async def _(session: CommandSession):
    param = session.current_arg_text.split()

    # help
    if len(param) == 0:
        await session.send(show_help())
        return

    # guide
    if len(param) == 1:
        await session.send(show_guide(param[0]))
        return





# 发起pve
@_cmd_group.command('boss')
async def _(session: CommandSession):
    ui = BotContextUI(session.bot, session.ctx)
    if session.ctx['message_type'] != 'group':
        return await ui.send('请不要孤身冒险！前往QQ群中，募集队友，和其他冒险者们一起战斗吧！')
    group_id = session.ctx['group_id']
    if group_id in _battles:
        return await ui.send('战斗还在进行中！')
    char = ui.retrieve('character')
    if char is None:
        return await ui.send('先创建一个角色，然后再来挑战吧！')

    boss, is_saved = _get_boss(group_id, lv_calc(char['exp']))
    if is_saved:
        ui.append('上次没人打的boss又回来啦！')
    else:
        ui.append('本次的boss是：')
    ui.append('强度参考值：%.0f' % (boss['power_rating'] * 1000))
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
    await ui.send('你提议开启一场boss战！其他人可以使用ksmgame-join来加入小队')

    asyncio.ensure_future(_remove_battle(session))


# 发起pvp
# @_cmd_group.command('pvp')
# async def _(session: CommandSession):
#     ui = BotContextUI(session.bot, session.ctx)
#     if session.ctx['message_type'] != 'group':
#         return await ui.send('只能在群里用（')
#     group_id = session.ctx['group_id']
#     if group_id in _battles:
#         return await ui.send('正打着呢（')
#     char = ui.retrieve('character')
#     if char is None:
#         return await ui.send('建角色，请（')

#     _battles[group_id] = {
#         'can_join': True,
#         'is_pvp': True,
#         'team_a': {},
#         'team_b': {},
#         'capacity_a': 4,
#         'capacity_b': 4
#     }
#     _battles[group_id]['team_a'][ui.uid()] = game_char_gen(char)
#     await ui.send('你发起了一场决斗，并加入了a队（')

#     asyncio.ensure_future(_remove_battle(session))


# 加入战斗
@_cmd_group.command('join')
async def _(session: CommandSession):
    ui = BotContextUI(session.bot, session.ctx)
    if session.ctx['message_type'] != 'group':
        return
    group_id = session.ctx['group_id']
    if group_id not in _battles:
        return await ui.send('现在还没有人募集队友，你可以使用"ksmgame-boss"发起一次挑战')
    bat = _battles[group_id]
    if not bat['can_join']:
        return await ui.send('战斗已经开始，让我们期待他们的胜利归来！')

    char = ui.retrieve('character')
    if char is None:
        return await ui.send('先创建一个角色，然后再来加入队伍吧！')

    if ui.uid() in bat['team_a'] or ui.uid() in bat['team_b']:
        return await ui.send('你已经在小队中了！')

    team = session.current_arg.lower()
    if bat['is_pvp']:
        if team not in ('a', 'b'):
            return await ui.send('只有a和b队（')
    else:
        if team not in ('', 'a'):
            return await ui.send('只能加入a队（')
        team = 'a'

    if len(bat[f'team_{team}']) >= bat[f'capacity_{team}']:
        return await ui.send('队伍满员')

    try:
        ui.run(_join, mutex_mode='group', args=(group_id, team, char))
    except BotContextUI.RunningException:
        await session.send(session.bot.config.SESSION_RUNNING_EXPRESSION)


# 转生
@_cmd_group.command('rebirth')
async def _(session: CommandSession):
    ui = BotContextUI(session.bot, session.ctx)
    char = ui.retrieve('character')
    if char is None:
        return await ui.send('你现在还没有角色，你可以直接新建一个角色！')

    last_rebirth = ui.retrieve('last_rebirth') or 0
    current_time = time.time()
    seconds_per_day = 24 * 60 * 60
    if int(current_time / seconds_per_day) - int(last_rebirth / seconds_per_day) < 1:
        return await ui.send('每天只能进行一次转生！')

    coin = int(ui.retrieve('talent_coin') or 0)
    acquire_coin = int(exp_to_talent_coin(char['exp']) * calc_passive(1, char, 'talent_coin_earn_rate'))
    ui.store('talent_coin', coin + acquire_coin)
    ui.store('character', None)
    ui.store('last_rebirth', current_time)
    await ui.send(f'你的角色化为了{acquire_coin}个天赋币')


# 天赋管理
@_cmd_group.command('talent')
async def _(session: CommandSession):
    try:
        BotContextUI(session.bot, session.ctx).run(upgrade_talent, mutex_mode='user')
    except BotContextUI.RunningException:
        await session.send(session.bot.config.SESSION_RUNNING_EXPRESSION)


@_cmd_group.command('reload')
async def _(_: CommandSession):
    data.reload()


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
    await asyncio.sleep(600)
    if group_id in _battles and _battles[group_id]['can_join']:
        del _battles[group_id]
        await session.send('在限定时间内没有募集齐成员……另择时间开启吧！')


async def _join(ui: BotContextUI, gid: int, team: str, char: dict):
    bat = _battles[gid]
    bat[f'team_{team}'][ui.uid()] = game_char_gen(char)
    if len(bat['team_a']) < bat['capacity_a'] or len(bat['team_b']) < bat['capacity_b']:
        return await ui.send(f'你加入了小队')

    bat['can_join'] = False
    ui.at_sender = False
    await ui.send('小队成员已经募集完毕，战斗即将开始！')
    await _play(ui, gid)


async def _play(ui: UI, gid: int):
    await asyncio.sleep(10)
    bat = _battles[gid]

    if not bat['is_pvp']:
        save = data.saves.group[str(gid)] or {}
        if save.pop('boss', None) is not None:
            data.saves.group[str(gid)] = save

    game = Gaming(bat['team_a'].values(), bat['team_b'].values(), ui)
    result, _ = await game.start()
    del _battles[gid]

    if bat['is_pvp']:
        # TODO pvp结果反馈
        pass
    else:
        if result == 'timeout':
            await ui.send('战斗超时！挑战失败了……遗憾')
        elif result == 'b_win':
            await ui.send('挑战者的队伍全灭，挑战失败……遗憾')
        elif result == 'a_win':
            exp_earn = sum(x['exp_earn'] for x in bat['team_b'].values())
            await ui.send('精彩的战斗！你们共同击败了boss！\n每个人获得了%d点经验！' % exp_earn)
            for uid in bat['team_a']:
                _give_exp(uid, exp_earn)
        elif result == 'all_dead':
            exp_earn = int(sum(x['exp_earn'] for x in bat['team_b'].values()) * 1.5)
            await ui.send('挑战者与Boss无一生还，这份舍己为人的精神被人们所歌颂，获得的经验值额外增加50%%！\n'
                          '每个人获得了%d点经验！' % exp_earn)
            for uid in bat['team_a']:
                _give_exp(uid, exp_earn)


def _give_exp(uid: int, amount: int):
    save = data.saves[str(uid)] or {}
    char = save['character']
    char['exp'] += int(amount * calc_passive(1, char, 'exp_earn_rate'))
    data.saves[str(uid)] = save
