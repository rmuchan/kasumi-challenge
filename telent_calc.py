import data
import matplotlib.pyplot as plt
numerical = data.numerical

"""
天赋树每层允许点的层数不一样，应该有标注。
每个属性的基础值最大 + 16  | 32级 + 0.5
每个属性的成长值最大 + 0.25  |  25级 + 0.05
防御基础值最大 + 2.7   | 27级 + 0.1
闪避 + 2.5% | 10级 + 0.25%
生命值提升(乘法) + 16%| 32级 + 0.5%
护盾、回复技能的倍率  + 10% | 20级 + 0.5%
魔法伤害倍率 + 10% | 20级 + 0.5%
增益效果倍率 + 10% | 20级 + 0.5%
暴击倍率 + 25% | 25级 + 1%
"""
# TODO 天赋树加成映射和天赋币消耗运算

def _recurrence(a_1: float, k: float, m: float, n: int) -> float:
    return (a_1 - m) * k ** (n - 1) + m * (k ** n - 1) / (k - 1)

if __name__ == '__main__':
    pass