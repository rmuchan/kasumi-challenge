from . import data, util
from .interact import UI


async def show_talent(ui: UI):
    player_talent = ui.retrieve('talent') or {}
    ordinal = ord('A')
    for attribute, param in data.talent.items():
        lvl = player_talent.get(attribute, 0)
        effect = param['effect']
        value = next(iter(effect.values())) if isinstance(effect, dict) else effect
        line = '{}.【{}】{}+{}'.format(chr(ordinal), param['name'], param['desc'],
                                     format(util.NumFormat(value * lvl), param['format']))
        if lvl < param['max_level']:
            line += ' (+{}) ●▶{}'.format(
                format(util.NumFormat(value), param['format']),
                util.recurrence(param['cost_base'], param['cost_ratio'], param['cost_grow'], lvl + 1)
            )
        else:
            line += ' (MAX)'
        ui.append(line)
        ordinal += 1
    await ui.send()


async def upgrade_talent(ui: UI):
    ui.append('你现有的天赋为：')
    await show_talent(ui)
    selection = await ui.input('选择想要强化的天赋',
                               is_valid=lambda x: len(x) == 1 and ord(x.upper()) - ord('A') in range(len(data.talent)))
    selection = ord(selection.upper()) - ord('A')
    key = list(data.talent)[selection]
    param = data.talent[key]
    player_talent = ui.retrieve('talent') or {}
    lvl = player_talent.get(key, 0)
    if lvl >= param['max_level']:
        await ui.send('该天赋已达到满级')
        return
    cost = util.recurrence(param['cost_base'], param['cost_ratio'], param['cost_grow'], lvl + 1)
    coin = ui.retrieve('talent_coin') or 0
    if cost > coin:
        await ui.send('天赋币不足')
        return
    player_talent[key] = lvl + 1
    coin -= cost
    ui.store('talent', player_talent)
    ui.store('talent_coin', coin)
    await ui.send('天赋升级成功！')


if __name__ == '__main__':
    pass
