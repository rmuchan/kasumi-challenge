from . import version


def show_help():
    return rf"""——-KASUMI CHALLENGE 帮助-——
> 当前版本：{get_ver()}
> 指令列表
    前缀："ksmgame"*无*空*格*间*隔*后接
    -help:      展示此帮助
    -log:        展示更新日志(在后面加数字"n"查看向前n版本的日志)
    -create:   创建新的角色
    -status:   查看角色信息
    -boss:     发起一场Boss战
    -pvp:       发起一场PVP，添加参数"real"会保留等级
    -join:       加入其它玩家的队伍
    -talent:    天赋管理
    -rebirth:   删除当前角色并获得天赋币(5小时内只能转生一次)
————————————
> 高级功能：
    -autolog:     版本更新时向群内推送更新日志(权限\Toggle用法)
    -help [关键词]: 查询有关游戏机制的详细解释(关键词前有空格)
    -check:        查看上一次的交互消息
————————————
❗️邀请bot进入您的群聊请发送邮件到"610@ice0.xyz"进行申请，否则不会通过。
————————————
👤如果您发现了任何文字、战斗数值等错误，或是对平衡性有任何建议，请发送邮件到"610@ice0.xyz"给开发者反馈，或者直接在GitHub中发起Issue或PR，感谢您的支持！
项目地址：https://github.com/rMuchan/kasumi-challenge
"""


def get_ver():
    return version.log_file[-1]['version']


def get_ver_idx(ver: str):
    for i in range(len(version.log_file) - 1, -1, -1):
        if ver == version.log_file[i]['version']:
            return i


def show_guide(key_word: str):
    S = ', '.join(['[%s]' % k for k in guide])
    return guide.get(key_word, f'没有"{key_word}"的描述，目前已添加的内容有：\n' + S)


def show_log(selection: int):
    if selection not in range(len(version.log_file)):
        return "还没有这么多版本"
    return version.log_file[-1 - selection]['version'] + "\n—-———-更新日志-———-—\n" + version.log_file[-1 - selection]['log']


guide = {}
guide['种族'] = """种族由玩家个人信息生成决定，无法改变。
种族会一定程度上改变玩家的初始属性，在新建角色时，观察说明可以得知自身种族对属性的影响。
在角色构筑时，选择适合种族特点的构筑是个不错的主意。"""
guide['经验'] = """每次成功击败Boss，玩家都会获得一定的经验，累积经验值可以提高玩家的等级。你可以使用"ksmgame-boss"指令发起一场Boss战。"""
guide['等级'] = """随着等级的提升，玩家的属性都会得到提升。相应地，玩家发起战斗时所需要挑战的Boss的等级也会随之调整。
你可以使用"ksmgame-status"查看角色所有属性。"""
guide['力量'] = """力量属性影响着角色的生命值。
此外，与敏捷共同影响着物理攻击伤害、与感知共同影响着恢复强度。"""
guide['敏捷'] = """敏捷属性影响着角色的防御和暴击伤害倍率。
此外，与力量共同影响着物理攻击伤害、与感知共同影响着法术倍率。"""
guide['感知'] = """感知属性影响着增益幅度和闪避率。
此外，与力量共同影响着恢复强度、与敏捷共同影响着法术倍率。"""
guide['攻击倍率'] = """攻击倍率在角色生成时随机决定。
通常，一个角色基础攻击为力量与敏捷进行调和的后一个数值乘以攻击倍率。。"""
guide['攻击'] = """攻击由力量与敏捷，以及攻击倍率决定。
普通攻击是唯一可以造成物理伤害的方式。"""
guide['恢复强度'] = """恢复强度由感知和力量共同决定。
恢复强度会影响受到治疗或生命窃取带来的治疗效果。"""
guide['法术倍率'] = """法术倍率由感知和敏捷共同决定。
角色造成的魔法伤害将会被法术倍率所影响，部分技能会在战斗中增强这个属性。
与攻击提升不同，法术倍率的提升是乘法累加的。"""
guide['增益幅度'] = """增益幅度由感知决定。
你受到的多数强化技能、由你施放的减益技能都会得到增益幅度的加成。你获得的护盾量也会得到增益幅度的加成。"""
guide['防御'] = """防御由力量和敏捷共同决定。
受到物理攻击时，防御将会减少一定的伤害。然而，打在护盾上的伤害无法减少。"""
guide['暴击伤害倍率'] = """暴击伤害倍率由敏捷决定。
暴击时，拥有更高暴击伤害倍率的角色会造成更高的伤害。"""
guide['魔法伤害'] = """魔法伤害会得到法术倍率的加成。
魔法伤害不会被防御衰减，会造成全额伤害。"""
guide['MP'] = """角色每轮行动将会获得一定范围内随机量的MP，此外，角色生命减少时，也会获得与伤害量相关的MP。
当MP达到满时，角色将会使用必杀技。"""
guide['主技能'] = """玩家在创建角色时需要选择三个技能中的一个作为主技能。
主技能将会有更短的冷却时间、更高的发动率和更小的MP消耗。
请选择和角色构筑核心相关的技能作为主技能。"""
guide['必杀技'] = """当MP达到满时，角色将会使用必杀技。必杀技拥有极其强大、以致于可以扭转战局的威力。使用必杀技过后MP将会被清空。"""
guide['闪避'] = """闪避由感知决定。
角色在被普通攻击时，有一定概率不会受到伤害。"""
guide['生命窃取'] = """角色普通攻击造成伤害后，根据造成伤害的一定比例回复生命，这个回复量会受到恢复强度的加成。
对护盾造成的伤害无法触发生命窃取。"""
guide['护盾'] = """角色一次只能拥有一个护盾，护盾无法叠加。
护盾优先于角色自身受到伤害，物理攻击会对护盾造成完全的伤害，不会受到角色防御的减值。"""
guide['天赋'] = """使用"ksmgame-talent"管理天赋，天赋是永久生效的。
注意，在已经拥有角色的情况下，升级天赋并不能为您当前的角色带来提升。"""
guide['天赋币'] = """使用"ksmgame-rebirth"将你的角色永久化为天赋币，这一操作不可逆。
当前角色的养成度越高，获得的天赋币数量越多。
你可以使用"ksmgame-talent"管理天赋进行升级，你之后的角色将会得到这些天赋加成。"""
guide['PVP'] = """玩家对抗模式，使用指令"ksmgame-pvp"发起。
发起者会自动加入A队，其他玩家可以使用"ksmgame-join a"或"ksmgame-join b"加入不同的队伍。
此外，可以使用"ksmgame-pvp real"发起一场不公平的PVP挑战，所有玩家会以当前等级加入PVP。
*PVP不会获得任何经验"""


