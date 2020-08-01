log_file = [
    {
        "version": "Alpha 0.0.7",
        "log": """
极大的平衡性调整：
法术构筑现在有更多样的叠加法术倍率的选择；
lv3中的沉默技能不再会为boss增加上百点防御
角色基础生命窃取从60%降低至40%
角色基础暴击率从16%降低至11%
角色基础暴击倍率从175%降低至160%
Huntars种族的暴击伤害倍率加成从100%下调至75%
角色基础闪避值有轻微的下调
被动中的暴击伤害倍率从40%下调至30%
被动中的基础生命加成从50下调至30
被动中的法术倍率增加从8%上调至9%
"终极射手"组技能的攻击提高量从期望90下调至期望30
由这些变动，重新设计了四个boss的属性
其中黑帮老大现在会拥有更高的防御力和更少的生命，以让法术构筑有更好的表现
增加了更新日志的功能
错误修复：
修复了敏捷和感知增加的被动技能异常地提高属性值的问题
修复了可能过高的减甲可能会导致伤害变为1的问题
"""
    },
    {
        "version": "Alpha 0.0.8",
        "log": """
游戏开始时玩家就会获得一定的MP，有机会在第一个回合使用技能
增加log向前查询的功能
错误修复：
修复了发起boss战可能会提前结束的错误
"""
    }, {
        "version": "Alpha 0.0.9",
        "log": """
lv2技能组的单体治疗目标从自身变为生命值最低的队友
【远距瞄准】技能增加一个期望40的攻击提升效果
若干涉及法术伤害提升的技能效果增加约50%左右的数值
"""
    }, {
        "version": "Alpha 0.0.10",
        "log": """
lv1增加"向阳"组效果，可以强化玩家的恢复强度。
lv3中的"净化"组技能，现在额外拥有一个降低目标恢复强度的效果
lv3中的"自然祝福"组技能，现在会为目标额外增加恢复强度
lv3中的"法力涌动"组技能，现在会为自身额外增加恢复强度
错误修复：
修复了多次攻击削弱buff导致攻击变为负数的情况，现在攻击最低为1
"""
    }, {
        "version": "Alpha 0.0.11",
        "log": """
【天使降临】组的治疗量从400下调至300，增加效果："使目标获得200点护盾并且在2回合内提升2点防御"
【强化治疗法术】组的治疗量从360上调到440
错误修复：
修复了lv3自然祝福恢复强度选择器错误的错误
"""
    }, {
        "version": "Alpha 0.1.0",
        "log": """
——战斗系统更新——
由生命值减少而增加的MP量从100%下调至75%
回合基础MP恢复从75上调至90
回合额外MP恢复范围从70上调至80
现在，所有的技能也会像普通攻击一样拥有一个效果数值的范围随机波动
——技能组更新——
lv3中[沉默]技能的持续时间从2c3下调至固定2回合
必杀技中的[终极射手]攻击提升效果从期望30上调至期望60，持续时间从1c2上调至固定2回合
增加了有关MP增加的技能效果，现在你可以在新建立的角色中选到这些技能
——Boss更新——
【黑帮老大】的基础攻击力期望从53.5上调至66
【黑帮老大】的[高爆手雷]技能伤害期望从220下调至200
【血色之鹰】的基础攻击力期望从185上调至215
【幽灵忍者】的攻击选择器从"RAND"变为"RAND_SAFE"，在仅有一个目标时不再多次攻击
添加了新的Boss【堕落教师】。和【幽灵忍者】一样，它是一个机制非常有趣，也有一点恶心的Boss，希望你们战斗愉快~
——用户系统更新——
现在Boss的强度参考值将会更加科学
现在转生的间隔由24小时减为12小时
在若干处增加了展示帮助的指令信息，方便新人熟悉系统
——系统更新——
现在玩家的状态效果使用了更好的管理机制，未来可能会推出分别针对增益效果和减益效果的技能
——错误修正——
当玩家在第30回合击败Boss时，系统会正常结算，不再会提示超时
"""
    }, {
        "version": "Alpha 0.1.1",
        "log": """
——Boss更新——
【堕落教师】的[偷换概念辩论]技能动态概率由10%上调至30%，移到2技能
【堕落教师】的[布置课堂作业]移到3技能
——错误修正——
Boss的强度参考值不再高到离谱
"""
    }, {
        "version": "Alpha 0.1.2",
        "log": """
——平衡更新——
修改了属性对应关系，现在：
敏捷将会影响防御和暴击倍率
力量只会影响生命上限
敏捷和力量共同影响攻击伤害
用户手册中的相关条目也对应地修改了
——错误修正——
修复了闪避不生效的错误

"""
    }, {
        "version": "Alpha 0.1.3",
        "log": """
——平衡更新——
【堕落教师】的生命窃取倍率从40%上调至90%，以平衡在沉默状态下战斗力过弱的问题
lv1中群体回复效果期望从25提升至38
lv1中自我治疗效果期望从70提升至80
lv1中自我护盾添加量从期望90上调至100
"""
    }, {
        "version": "Alpha 0.1.4",
        "log": """
——平衡更新——
【堕落教师】的基础攻击期望从195上调至210
【堕落教师】的基础防御期望从2.65下调至1.65
【堕落教师】的生命基础值期望从455下调至435
【堕落教师】的恢复强度期望从108%下调至102%
【堕落教师】的法术强度期望从105%下调至95%
【堕落教师】的生命窃取倍率从90%下调至70%
【堕落教师】的[错题审判]生命回复期望从530下调至330
【堕落教师】的[布置课堂作业]法术伤害期望从70上调至170
【堕落教师】的[自我否定误导]更名为[点名批评]，法术伤害期望从365上调至440，额外增加一个生命恢复效果
"""
    },{
        "version": "Alpha 0.1.5",
        "log": """
——平衡更新——
技能组中效果为百分比攻击提升技能现在拥有更高的倍率和更长的持续时间
lv3中造成魔法伤害并提升法术倍率的技能伤害期望从110下调至100，法术倍率提高期望从12.5%上调至20.5%，持续时间由8c10下调至6c8
lv3中提升法术倍率并提升恢复强度的技能法术倍率提高期望从29.5%上调至42%
增加了[迅猛冲拳]组技能，在当回合提升自身攻击并进行一次普通攻击
[天使降临]技能的治疗量期望从300下调至260
[守护天使]技能的护盾量期望从200下调至160
[魔力过载]技能的法术倍率提高期望从99%上调至120%，额外为自己添加期望170的护盾
"""
    },{
        "version": "Alpha 0.1.6",
        "log": """
——【黑帮老大】平衡性调整——
攻击力由期望66下调至53
[机枪扫射]由6次攻击上调至7次
防御基础值由期望3.75下调至3.05
增益幅度由120%下调至110%
暴击伤害倍率由150%上调至210%
暴击率由12%上调至14%
[高爆手雷]伤害由期望200下调至190
[高精度瞄准镜]暴击率提高从期望16%上调至55%
[寻找掩体]闪避提升由15%提升至50%，额外为自己添加一个期望220的护盾
——技能组调整——
lv1中的MP增加技能由期望47.5上调至90
lv2中群体MP增加技能由期望47.5上调至65
lv3中伤害队友并增加MP的技能，MP增加期望由160上调至230
"""
    }
]
