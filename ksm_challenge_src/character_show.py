from .attr_calc import game_char_gen, lv_calc, exp_overlay_list
from .character import calc_passive
from .interact import UI
from .skill import get_skill_desc


async def show_chara_info(ui: UI):
    char = ui.retrieve('character')
    if char is None:
        await ui.send('你还没有创建角色')
        return
    game_char = game_char_gen(char)

    ui.append('------玩家信息------')
    ui.append('名字：%s | 种族：%s' % (game_char['name'], char['race']))
    lv = lv_calc(char['exp'])
    ui.append('等级：%d (%d/%d)' % (lv, char['exp'] - exp_overlay_list[lv-1], exp_overlay_list[lv] - exp_overlay_list[lv-1]))
    ui.append('力量：%.0f | 敏捷：%.0f' % (game_char['str'], game_char['int']))
    ui.append('感知：%.0f | 生命：%.0f' % (game_char['per'], game_char['HP']))
    ui.append('攻击：%.0f | 防御：%.1f' % (game_char['attack'], game_char['defence']))
    ui.append('恢复强度：{:.0%}'.format(game_char['recover_rate']))
    ui.append('法术倍率：{:.0%}'.format(game_char['spell_rate']))
    ui.append('增益幅度：{:.0%}'.format(game_char['buff_rate']))
    ui.append('暴击倍率：{:.0%}'.format(game_char['crit_rate']))
    ui.append('生命窃取：{:.0%}'.format(game_char['life_steal_rate']))
    ui.append('闪避率：{:.1%}'.format(game_char['dodge']))
    ui.append('------技能组------')
    skill_chance_boost = calc_passive(1, char, 'skill_chance_boost')
    mp_consume_dec = calc_passive(1, char, 'mp_consume_dec')
    ui.append('必杀技：\n' + get_skill_desc(game_char['unique'], True, skill_chance_boost, mp_consume_dec))
    ui.append('主技能：\n' + get_skill_desc(game_char['skills'][0], False, skill_chance_boost, mp_consume_dec))
    ui.append('技能2：\n' + get_skill_desc(game_char['skills'][1], False, skill_chance_boost, mp_consume_dec))
    ui.append('技能3：\n' + get_skill_desc(game_char['skills'][2], False, skill_chance_boost, mp_consume_dec))
    ui.append('被动加成：\n' + char['passive']['desc'])
    await ui.send()
