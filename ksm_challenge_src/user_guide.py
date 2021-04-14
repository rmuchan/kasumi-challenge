from . import version


def show_help():
    return rf"""——-KASUMI CHALLENGE 帮助-——
> 当前版本：{get_ver()}
> 指令列表
    前缀："ksmgame"无空格间隔后接
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
👤如果您发现了任何文字、战斗数值等错误，或是对平衡性有任何建议，请直接在GitHub中发起Issue或PR，感谢您的支持！
项目地址：https://github.com/rmuchan/kasumi-challenge
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
guide['力量'] = """力量属性影响着角色的生命值和暴击倍率。
此外，与敏捷共同影响着物理攻击伤害、与感知共同影响着恢复强度。"""
guide['敏捷'] = """敏捷属性影响着角色的闪避率。
此外，与力量共同影响着物理攻击伤害、与感知共同影响着法术倍率。"""
guide['感知'] = """感知属性影响着增益幅度和防御。
此外，与力量共同影响着恢复强度、与敏捷共同影响着法术倍率。"""
guide['攻击倍率'] = """攻击倍率在角色生成时随机决定。
通常，一个角色的基础攻击与力量、敏捷和攻击倍率相关。"""
guide['攻击'] = """攻击由力量和敏捷，以及攻击倍率决定。
普通攻击是唯一可以造成物理伤害的方式。"""
guide['恢复强度'] = """恢复强度由感知和力量共同决定。
恢复强度会影响受到治疗或生命窃取带来的治疗效果。"""
guide['法术倍率'] = """法术倍率由感知和敏捷共同决定。
角色造成的魔法伤害将会被法术倍率所影响，部分技能会在战斗中增强这个属性。
与攻击提升不同，法术倍率的提升是乘法累加的。"""
guide['增益幅度'] = """增益幅度由感知决定。
你受到的多数强化技能、由你施放的减益技能都会得到增益幅度的加成。你获得的护盾量也会得到增益幅度的加成。
你为其他角色释放的治疗技能效果会受到你的增益幅度和目标的恢复强度的共同影响。"""
guide['防御'] = """防御由感知决定。
受到物理攻击时，防御将会减少一定的伤害。然而，打在护盾上的伤害无法减少。"""
guide['暴击伤害倍率'] = """暴击伤害倍率由力量决定。
暴击时，拥有更高暴击伤害倍率的角色会造成更高的伤害。"""
guide['魔法伤害'] = """魔法伤害会得到法术倍率的加成。
魔法伤害不会被防御衰减，会造成全额伤害。"""
guide['穿刺伤害'] = """穿刺伤害通常由一些涉及生命值百分比的技能造成。穿刺伤害会无视护盾直接地对生命值造成伤害。"""
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
guide['急速冷却'] = """在该状态下，角色的所有技能每回合将会额外减少1的冷却。"""


guide['食尸恶灵'] = """————食尸恶灵————
【普通攻击】
 [饕餮]
    - 对3个敌方目标造成伤害。
【必杀技】
 [猎杀形态]
    - 大幅度提高自身闪避率，大幅度降低敌方全体的法术倍率，沉默自身。
【技能组】
 [杀戮盛宴]
    - 降低敌方全体防御，提升自身生命窃取倍率，沉默自身1回合。
 [恐吓]
    - 对2个敌方目标造成中额魔法伤害，并大幅度降低其攻击。
 [肢体重构]
    - 清除自身所有的状态效果，小额回复自身生命。"""

guide['魔化蜂王'] = """————魔化蜂王————
【普通攻击】
 [工蜂追杀]
    - 对1个敌方目标造成伤害。
【必杀技】
 [全蜂出动]
    - 获得大量护盾，中幅度提高自身闪避率，大幅度降低自身防御，沉默敌方全体。
【技能组】
 [蜂王作战浓浆]
    - 回复自身生命，获得中额护盾，大幅度提高自身闪避率。
 [蜂群战术]
    - 对攻击最高的2名敌方目标造成小额魔法伤害，并大幅度降低其中攻击最高的1名敌方目标的攻击。
 [蜂群之噬]
    - 进行7次随机目标的魔法攻击，每次伤害有所差异。
【特性】
    - 工蜂追杀会攻击生命最低的敌方目标。"""

guide['血色之鹰'] = """————血色之鹰————
【普通攻击】
 [爪击]
    - 对3个敌方目标造成伤害。
【必杀技】
 [血色凋零]
    - 对敌方全体造成中额魔法伤害，随机1个敌方目标额外受到一次中额魔法伤害。
【技能组】
 [狂怒龙卷]
    - 对随机3个敌方目标造成小额魔法伤害，并降低其攻击。
 [刺耳鹰唳]
    - 对随机3个敌方目标造成中额魔法伤害，并降低其防御。
 [羽栖]
    - 大幅度回复自身生命，提升自身防御。"""

guide['黑帮老大'] = """————黑帮老大————
【普通攻击】
 [机枪扫射]
    - 进行6次攻击，每次造成小额伤害。
【必杀技】
 [人肉炸弹]
    - 对敌方全体和自身造成高额魔法伤害。
【技能组】
 [高爆手雷]
    - 对敌方全体造成高额魔法伤害。
 [高精度瞄准镜]
    - 提升自身攻击与暴击率。
 [寻找掩体]
    - 提升自身防御与闪避率，获得中额护盾。"""

guide['血炎魔王'] = """————血炎魔王————
【普通攻击】
 [炎斧挥砍]
    - 对1个敌方目标造成伤害。
【必杀技】
 [烈火重燃]
    - 清除自身所有的状态效果，获得火焰附魔。
【技能组】
 [魔焰狂热]
    - 回复自身生命，将MP恢复至满。
 [战斗狂热]
    - 获得攻击标记，提升自身生命窃取倍率。
 [毁灭横扫]
    - 对敌方全体进行一次伤害更低的炎斧挥砍。
【特性】
    - 血炎魔王每次攻击都会降低自身的法术倍率。"""

guide['邪魔术士'] = """————邪魔术士————
【普通攻击】
 [利刃斩击]
    - 对2个敌方目标造成伤害。
【必杀技】
 [狂乱邪焰]
    - 对敌方全体造成高额魔法伤害。
【技能组】
 [邪能屏障]
    - 获得大量护盾。
 [腐化双珠]
    - 对2个敌方目标造成小额魔法伤害，降低其防御。
 [灭亡之触]
    - 对1个敌方目标造成高额魔法伤害。"""

guide['幽灵忍者'] = """————幽灵忍者————
【普通攻击】
 [突刺]
    - 对2个敌方目标造成伤害。
【必杀技】
 [锁喉]
    - 对1个敌方目标造成高额魔法伤害。
【技能组】
 [暗影斗篷]
    - 获得护盾，提高自身攻击。
 [刃舞]
    - 对敌方全体造成小额魔法伤害。
 [遁入暗影]
    - 提高自身防御，获得小额治疗，降低敌方全体防御。
【特性】
    - 幽灵忍者拥有非常高的闪避率和暴击率，每进行一次攻击，都会提高自身的暴击伤害倍率。"""

guide['灵魂行者'] = """————灵魂行者————
【普通攻击】
 [破坏契约]
    - 对敌方全体造成伤害。
【必杀技】
 [灵魂契约]
    - 与敌方生命最高的目标交换生命百分比，如果自身生命百分比已大于目标，则直接造成高额的魔法伤害。
【技能组】
 [守护契约]
    - 献祭自身一部分生命，获得高额护盾与闪避率提升效果。
 [毁灭契约]
    - 对敌方全体造成高额魔法伤害。
 [亢奋契约]
    - 献祭自身一部分生命，提高自身攻击，获得MP。
【特性】
    - 灵魂行者的穿刺伤害不会将自己杀死。"""

guide['罪罚萨满'] = """————罪罚萨满————
【普通攻击】
 [降罪]
    - 对敌方全体造成伤害。
【必杀技】
 [救赎]
    - 治疗己方全体，为己方队伍召唤一个烈焰图腾。
【技能组】
 [召唤烈焰图腾]
    - 为己方队伍召唤一个烈焰图腾，它会对敌方目标造成中额魔法伤害。
 [召唤治愈图腾]
    - 为己方队伍召唤一个治愈图腾，它会治疗己方目标。
【特性】
    - 图腾的技能会消耗自身巨大的MP，所以通常不会使用必杀技，但是在受到高额伤害导致MP充满的情况下，图腾会使用强大的必杀技，这会摧毁自身。"""

guide['堕落教师'] = """————堕落教师————
【普通攻击】
 [腐化粉笔飞弹]
    - 对3个敌方目标造成伤害，降低其恢复强度。
【必杀技】
 [点名批评]
    - 对敌方生命最低的目标造成高额魔法伤害，恢复自身生命。
【技能组】
 [错题审判]
    - 窃取1个敌方目标的MP，以一定倍率恢复自身的MP，同时获得护盾。
 [偷换概念辩论]
    - 沉默3个敌方目标，并对其造成小额魔法伤害。
 [布置课堂作业]
    - 对敌方3个目标造成中额魔法伤害，大幅度降低其恢复强度。"""

guide['霆'] = """————霆————
【普通攻击】
 [线路短接]
    - 对1个敌方目标造成伤害，同时对2个敌方目标造成小额魔法伤害。
【必杀技】
 [电力充沛]
    - 霆不再使用必杀技，他的MP越多，他的法术倍率与增益幅度越高。
【技能组】
 [磁场屏障]
    - 获得高额护盾和MP。
 [电力过载]
    - 失去自身一部分生命，提高自身攻击。
【特性】
    - 霆每回合会为自身添加逆向电流效果，每回合第一次使用普通攻击击中霆的角色将会受到中额魔法伤害。
    - 霆每受到一次普通攻击，失去一定量的MP。"""