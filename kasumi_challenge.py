import _thread
import asyncio
import atexit
import json
import os
import random
import time

from flask import Flask, request
from nonebot import CommandGroup, on_natural_language, NLPSession, CommandSession
from nonebot import permission as perm
from nonebot.session import BaseSession

from .ksm_challenge_src.Gaming import Gaming
from .ksm_challenge_src.attr_calc import game_char_gen, lv_calc
from .ksm_challenge_src.boss_gen import boss_gen
from .ksm_challenge_src.bot_ui import BotContextUI
from .ksm_challenge_src.character import create_character, print_character, exp_to_talent_coin, calc_passive
from .ksm_challenge_src.character_show import show_chara_info
from .ksm_challenge_src.data import data
from .ksm_challenge_src.interact import UI, output
from .ksm_challenge_src.talent_calc import upgrade_talent
from .ksm_challenge_src.user_guide import *
from .ksm_challenge_src.version import great_update_ver

app = Flask(__name__)


@app.route('/create_info', methods=['GET'])
def create_info():
    print(request.form)
    return '<p>' + output.get(int(request.args.get('qid', 0)), ' ').replace('\n', '</br>') + '</p>'


def web_server():
    app.run(host='127.0.0.1', port=9286)


_thread.start_new_thread(web_server, ())


def conf_read(name):
    # 读配置文件
    with open('%s/configs/%s' % (os.path.dirname(__file__), f'{name}_config.json')) as FILE:
        config_dict = json.loads(FILE.read())
    return config_dict


def conf_write(name, dict_):
    os.makedirs(os.path.join(os.path.dirname(__file__), 'configs'), 0o755, exist_ok=True)
    with open('%s/configs/%s' % (os.path.dirname(__file__), f'{name}_config.json'), 'w+', encoding='utf-8') as f:
        f.write(json.dumps(dict_, sort_keys=False, indent=4, ensure_ascii=False))


_battles = {}
_cmd_group = CommandGroup('ksmgame', only_to_me=False)

_anonymous_alert = '不要匿名' * 6

try:
    config = conf_read('ksmgame')
except:
    config = dict(enabled_group=[], pre_version="")
    conf_write('ksmgame', config)


@on_natural_language(only_to_me=False)
async def _(session: NLPSession):
    global config
    if get_ver() != config['pre_version']:
        config['pre_version'] = get_ver()
        conf_write('ksmgame', config)
        await send_to_all(session.bot, show_log(0))


@_cmd_group.command('warn', permission=perm.SUPERUSER)
async def _(session: CommandSession):
    await send_to_all(session.bot, '提示：bot即将进入功能维护，所有功能将会暂时中止。')
    for bat in _battles.values():
        for uid in bat['team_a']:
            _reset_join_time(uid)
        for uid in bat['team_b']:
            _reset_join_time(uid)
    await session.send('发送完成')


@_cmd_group.command('done', permission=perm.SUPERUSER)
async def _(session: CommandSession):
    await send_to_all(session.bot, 'bot维护完成，角色创建被中断的玩家可以再次使用create命令继续创建进程。')
    await session.send('发送完成')


async def send_to_all(bot, msg):
    for gid in config['enabled_group']:
        await asyncio.sleep(0.1)
        try:
            await bot.send_group_msg(group_id=int(gid), message=msg)
        except:
            print(f'这个群已经不在了！:{gid}')



# 查看消息记录
@_cmd_group.command('check')
async def _(session: CommandSession):
    if session.ctx['user_id'] == 80000000:
        return await session.send(_anonymous_alert)
    await session.send(f'http://ksmgame-check.ice0.xyz/create_info?qid={session.ctx["user_id"]}')


# 自动推送日志
@_cmd_group.command('autolog', permission=perm.SUPERUSER | perm.GROUP_ADMIN)
async def _(session: CommandSession):
    # 忽略私聊消息
    if session.ctx['message_type'] != 'group':
        return

    param = session.current_arg_text.split()

    global config

    gid = str(session.ctx.get('group_id', '000000000'))

    if len(param) == 0:
        if gid in config['enabled_group']:
            config['enabled_group'].remove(gid)
            conf_write('ksmgame', config)
            return await session.send('🔴当游戏版本更新时，本群不再自动推动更新日志，您可以使用"ksmgame-log"指令手动查询最新更新日志。')
        else:
            config['enabled_group'].append(gid)
            conf_write('ksmgame', config)
            return await session.send('🟢当游戏版本更新时，本群将自动推动更新日志，您也可以使用"ksmgame-log"指令手动查询最新更新日志。')

    if len(param) == 1:
        if param[0] == 'on':
            config['enabled_group'].append(gid)
            conf_write('ksmgame', config)
            return await session.send('🟢当游戏版本更新时，本群将自动推动更新日志，您也可以使用"ksmgame-log"指令手动查询最新更新日志。')
        elif param[0] == 'off':
            config['enabled_group'].remove(gid)
            conf_write('ksmgame', config)
            return await session.send('🔴当游戏版本更新时，本群不再自动推动更新日志，您可以使用"ksmgame-log"指令手动查询最新更新日志。')

    return await session.send('指令错误。使用"ksmgame-autolog on/off"来管理更新日志自动推送功能')


# 新建
@_cmd_group.command('create')
async def _(session: CommandSession):
    if session.ctx['user_id'] == 80000000:
        return await session.send(_anonymous_alert)

    async def create(ui: UI):
        if ui.retrieve('character') is not None:
            await ui.send('你已经拥有了一个角色！你可以使用ksmgame-status来查看属性')
            return
        pc = ui.retrieve('proto_character')
        if pc is not None:
            create_ver = get_ver_idx(pc.get('game_version')) or 0
            min_ver = get_ver_idx(great_update_ver)
            if create_ver < min_ver:
                ui.store('proto_character', None)
        char = await create_character(ui)
        ui.store('character', char)
        ui.store('proto_character', None)
        ui.append('角色创建完成！')
        await show_chara_info(ui)

    try:
        BotContextUI(session.bot, session.ctx).run(create, mutex_mode='user')
    except BotContextUI.RunningException:
        await session.send(session.bot.config.SESSION_RUNNING_EXPRESSION)


# 查询角色信息
@_cmd_group.command('status')
async def _query(session: CommandSession):
    if session.ctx['user_id'] == 80000000:
        return await session.send(_anonymous_alert)
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


@_cmd_group.command('log')
async def _(session: CommandSession):
    arg = int(session.current_arg) if session.current_arg.isdigit() else 0
    await session.send(show_log(arg))


# 发起pve
@_cmd_group.command('boss')
async def _(session: CommandSession):
    if session.ctx['user_id'] == 80000000:
        return await session.send(_anonymous_alert)

    ui = BotContextUI(session.bot, session.ctx)
    if session.ctx['message_type'] != 'group':
        return await ui.send('请不要孤身冒险！前往QQ群中，募集队友，和其他冒险者们一起战斗吧！')
    group_id = session.ctx['group_id']
    if group_id in _battles:
        if _battles[group_id].get('is_pvp'):
            return await ui.send('对决正在进行中，你可以使用"ksmgame-join a/b"加入队伍！')
        else:
            return await ui.send('冒险正在进行中，你可以使用"ksmgame-join"加入队伍！')

    char, err = _check_join(ui)
    if err is not None:
        return await ui.send(err)

    if session.current_arg_text and await perm.check_permission(session.bot, session.event, perm.SUPERUSER):
        force_boss = session.current_arg_text
    else:
        force_boss = None

    boss, is_saved = _get_boss(group_id, lv_calc(char['exp']), force_boss)

    bat = {
        'can_join': True,
        'is_pvp': False,
        'team_a': {},
        'team_b': {-idx: item for idx, item in enumerate(boss['bosses'])},
        'capacity_a': 4,
        'capacity_b': 1
    }
    bat['team_a'][ui.uid()] = game_char_gen(char)
    _battles[group_id] = bat

    if is_saved:
        ui.append('上次没人打的boss又回来啦！')
    else:
        ui.append('本次的boss是：')
    ui.append(boss['desc'])
    await ui.send('强度参考值：%.0f' % (boss['final_rating'] * 10))
    await ui.send('你提议开启一场boss战！其他人可以使用ksmgame-join来加入小队')

    asyncio.ensure_future(_remove_battle(session, bat))


# 发起pvp
@_cmd_group.command('pvp')
async def _(session: CommandSession):
    if session.ctx['user_id'] == 80000000:
        return await session.send(_anonymous_alert)

    ui = BotContextUI(session.bot, session.ctx)
    if session.ctx['message_type'] != 'group':
        return
    group_id = session.ctx['group_id']
    if group_id in _battles:
        if _battles[group_id].get('is_pvp'):
            return await ui.send('对决正在进行中，你可以使用"ksmgame-join a/b"加入队伍！')
        else:
            return await ui.send('冒险正在进行中，你可以使用"ksmgame-join"加入队伍！')

    char, err = _check_join(ui)
    if err is not None:
        return await ui.send(err)

    is_real = session.current_arg.lower() == 'real'

    bat = {
        'can_join': True,
        'is_pvp': True,
        'team_a': {},
        'team_b': {},
        'capacity_a': 4,
        'capacity_b': 4,
        'is_real': is_real
    }
    bat['team_a'][ui.uid()] = game_char_gen(char, real_mode=is_real)
    _battles[group_id] = bat

    await ui.send('你提议开启一场PVP并自动加入了a队！其他人可以使用"ksmgame-join a"来和发起者组队，或是使用"ksmgame-join b"加入对面阵营。')

    asyncio.ensure_future(_remove_battle(session, bat))


# 加入战斗
@_cmd_group.command('join')
async def _(session: CommandSession):
    if session.ctx['user_id'] == 80000000:
        return await session.send(_anonymous_alert)

    ui = BotContextUI(session.bot, session.ctx)
    if session.ctx['message_type'] != 'group':
        return
    group_id = session.ctx['group_id']
    if group_id not in _battles:
        return await ui.send('现在还没有人募集队友，你可以使用"ksmgame-boss"发起一次挑战')
    bat = _battles[group_id]
    if not bat['can_join']:
        return await ui.send('战斗已经开始，让我们期待他们的胜利归来！')

    char, err = _check_join(ui, bat, False)
    if err is not None:
        return await ui.send(err)

    team = session.current_arg.lower()
    if bat['is_pvp']:
        if not team:
            can_join_a = len(bat['team_a']) < bat['capacity_a']
            can_join_b = len(bat['team_b']) < bat['capacity_b']
            if can_join_a and can_join_b:
                team = random.choice(('a', 'b'))
            elif can_join_a:
                team = 'a'
            else:
                team = 'b'
        elif team not in ('a', 'b'):
            return await ui.send('参数只支持a或b，不要当测试工程师了！')
    else:
        team = 'a'

    if len(bat[f'team_{team}']) >= bat[f'capacity_{team}']:
        return await ui.send('这个队伍已经满员了')

    try:
        ui.run(_join, mutex_mode='group', args=(group_id, team, char, bat['is_pvp']))
    except BotContextUI.RunningException:
        await session.send(session.bot.config.SESSION_RUNNING_EXPRESSION)


# 转生
@_cmd_group.command('rebirth')
async def _(session: CommandSession):
    if session.ctx['user_id'] == 80000000:
        return await session.send(_anonymous_alert)

    ui = BotContextUI(session.bot, session.ctx)
    char = ui.retrieve('character')
    if char is None:
        return await ui.send('你现在还没有角色，你可以使用"ksmgame-create"创建新的角色！')

    last_rebirth = ui.retrieve('last_rebirth') or 0
    current_time = time.time()
    rebirth_interval = 5 * 60 * 60
    if current_time - last_rebirth < rebirth_interval:
        next_rebirth = last_rebirth + rebirth_interval
        next_rebirth_str = time.strftime('%H:%M', time.localtime(next_rebirth))
        return await ui.send(f'每5小时只能进行一次转生\n你可以在{next_rebirth_str}之后再次转生')

    coin = int(ui.retrieve('talent_coin') or 0)
    acquire_coin = int(exp_to_talent_coin(char['exp']) * calc_passive(1, char, 'talent_coin_earn_rate'))
    ui.store('talent_coin', coin + acquire_coin)
    ui.store('character', None)
    ui.store('last_rebirth', current_time)
    await ui.send(f'你的角色化为了{acquire_coin}个天赋币')


# 天赋管理
@_cmd_group.command('talent')
async def _(session: CommandSession):
    if session.ctx['user_id'] == 80000000:
        return await session.send(_anonymous_alert)

    try:
        BotContextUI(session.bot, session.ctx).run(upgrade_talent, mutex_mode='user')
    except BotContextUI.RunningException:
        await session.send(session.bot.config.SESSION_RUNNING_EXPRESSION)


# 管理员功能：重新加载数据
@_cmd_group.command('reload', permission=perm.SUPERUSER)
async def _(_: CommandSession):
    data.reload()


# 管理员功能：重设所有玩家转生限制
@_cmd_group.command('reset', permission=perm.SUPERUSER)
async def _(_: CommandSession):
    for uid in data.saves.dir():
        save = data.saves[uid]
        save.pop('last_rebirth', None)
        data.saves[uid] = save


def _get_boss(gid: int, lvl: int, force_boss: str):
    save = data.saves.group[str(gid)] or {}
    if not force_boss:
        boss = save.get('boss')
        if boss is not None:
            return boss, True

    pool = data.boss_pool
    template = pool[force_boss or random.choice(pool.dir())]
    boss = boss_gen(template, lvl)
    save['boss'] = boss
    data.saves.group[str(gid)] = save
    return boss, False


async def _remove_battle(session: BaseSession, bat: dict):
    group_id = session.ctx['group_id']
    await asyncio.sleep(600)
    if _battles.get(group_id) is bat and bat['can_join']:
        for uid in _battles[group_id]['team_a']:
            _reset_join_time(uid)
        for uid in _battles[group_id]['team_b']:
            _reset_join_time(uid)
        del _battles[group_id]
        await session.send('在限定时间内没有募集齐成员……另择时间开启吧！')


def _check_join(ui: BotContextUI, bat: dict = None, set_join: bool = True):
    char = ui.retrieve('character')
    if char is None:
        return None, '你还未拥有一个角色！\n你可以使用"ksmgame-help"了解游戏的使用方法！'
    create_ver = get_ver_idx(char.get('game_version')) or 0
    min_ver = get_ver_idx(great_update_ver)
    if create_ver < min_ver:
        return None, '角色存档数据格式变动，请重新创建角色。'
    if bat is not None and (ui.uid() in bat['team_a'] or ui.uid() in bat['team_b']):
        return None, '你已经在小队中了！'
    if time.time() - (ui.retrieve('last_join') or 0) < 1120:
        return None, '你同时只能参与一场战斗！'
    if set_join:
        ui.store('last_join', time.time())
    return char, None


async def _join(ui: BotContextUI, gid: int, team: str, char: dict, show_team: bool):
    bat = _battles[gid]
    game_char = game_char_gen(char, real_mode=bat.get('is_real', True))
    bat[f'team_{team}'][ui.uid()] = game_char
    ui.store('last_join', time.time())
    if len(bat['team_a']) < bat['capacity_a'] or len(bat['team_b']) < bat['capacity_b']:
        name = game_char['name']
        return await ui.send('你的角色"{}"加入了{}'.format(name, f'{team}队' if show_team else '小队'))

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
    try:
        result, _ = await game.start()
    finally:
        del _battles[gid]

    if bat['is_pvp']:
        for uid in bat['team_a']:
            _reset_join_time(uid)
        for uid in bat['team_b']:
            _reset_join_time(uid)
        if result == 'timeout':
            await ui.send('战斗超时！你们不要再打啦，这样是打不死人的！')
        elif result == 'b_win':
            await ui.send('恭喜B队获胜！')
        elif result == 'a_win':
            await ui.send('恭喜A队获胜！')
        elif result == 'all_dead':
            await ui.send('可以说战斗是很惨烈了。无人生还……')
    else:
        for uid in bat['team_a']:
            _reset_join_time(uid)
        if result == 'timeout':
            await ui.send('战斗超时！挑战失败了……遗憾\n使用指令"ksmgame-help"了解更多的游戏机制吧！')
        elif result == 'b_win':
            await ui.send('挑战者的队伍全灭，挑战失败……遗憾\n使用指令"ksmgame-help"了解更多的游戏机制吧！')
        elif result == 'a_win':
            exp_earn = sum(x.get('exp_earn', 0) for x in bat['team_b'].values())
            await ui.send('精彩的战斗！你们共同击败了boss！\n每个人获得了%d点经验！' % exp_earn)
            for uid in bat['team_a']:
                _give_exp(uid, exp_earn)
        elif result == 'all_dead':
            exp_earn = int(sum(x.get('exp_earn', 0) for x in bat['team_b'].values()) * 1.5)
            await ui.send('挑战者与Boss无一生还，这份舍己为人的精神被人们所歌颂，获得的经验值额外增加50%%！\n'
                          '每个人获得了%d点经验！' % exp_earn)
            for uid in bat['team_a']:
                _give_exp(uid, exp_earn)


def _give_exp(uid: int, amount: int):
    save = data.saves[str(uid)] or {}
    char = save.get('character')
    if isinstance(char, dict):
        char['exp'] += int(amount * calc_passive(1, char, 'exp_earn_rate'))
        data.saves[str(uid)] = save


def _reset_join_time(uid: int):
    save = data.saves[str(uid)] or {}
    if save.pop('last_join', None) is not None:
        data.saves[str(uid)] = save


@atexit.register
def _():
    for bat in _battles.values():
        for uid in bat['team_a']:
            _reset_join_time(uid)
        for uid in bat['team_b']:
            _reset_join_time(uid)
