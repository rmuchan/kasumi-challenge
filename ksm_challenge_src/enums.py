from enum import Enum, auto


# Buff类的声明
class BuffProperty:
    def __init__(self, is_debuff: bool):
        self.is_debuff = is_debuff

# 全部的Buff类型
class Buff(Enum):
    DEFENCE_ENHANCED = BuffProperty(False)


# 为_life_hurt和recover函数的参数设计的Enum
class PercentageType(Enum):
    SET = auto()    # 将生命值强行设定为最大生命值*param的数字。伤害时要求param小于当前百分比，否则不会造成伤害；恢复时要求param大于当前百分比，否则不会恢复
    DEC = auto()    # 受到生命值最大值*param的穿刺伤害

