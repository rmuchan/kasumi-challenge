from .attr_calc import game_char_gen
from .interact import UI
from .skill import get_skill_desc


async def show_chara_info(ui: UI):
    char = ui.retrieve('character')
    if char is None:
        await ui.send('你还没有创建角色')
        return
    char = game_char_gen(char)

    ui.append('------玩家信息------')
    ui.append('名字：%s | 种族：%s' % (char['name'], char['race']))
    ui.append('力量：%.0f | 敏捷：%.0f' % (char['str'], char['int']))
    ui.append('感知：%.0f | 生命：%.0f' % (char['per'], char['HP']))
    ui.append('攻击：%.0f | 防御：%.1f' % (char['attack'], char['defence']))
    ui.append('恢复强度：{:.0%}'.format(char['recover_rate']))
    ui.append('法术倍率：{:.0%}'.format(char['spell_rate']))
    ui.append('增益幅度：{:.0%}'.format(char['buff_rate']))
    ui.append('暴击倍率：{:.0%}'.format(char['crit_rate']))
    ui.append('生命窃取：{:.0%}'.format(char['life_steal_rate']))
    ui.append('闪避率：{:.1%}'.format(char['dodge']))
    ui.append('------技能组------')
    ui.append('主技能：\n' + get_skill_desc(char['skill_1'], is_unique=False))
    ui.append('副技能：\n' + get_skill_desc(char['skill_2'], is_unique=False))
    ui.append('小技能：\n' + get_skill_desc(char['skill_3'], is_unique=False))
    ui.append('必杀技：\n' + get_skill_desc(char['unique'], is_unique=True))
    await ui.send()
