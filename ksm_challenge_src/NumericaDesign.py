import random

from ksm_challenge_src.data import data

numerical = data.numerical

level = [1, 10, 20, 30, 40]

"""
属性
"""
attr_rate = 1.01
attr_add = 1.2
attr_base = 50

hp_base = 160
hp_add = 3.6
hp_lv_rate = 1.003
hp_rate = 2.4
"""
伤害公式
"""
def_rate = 0.27
atk_rate = 3.2
def_base = 1.2


def atkCalc(lv):
    # print('atkCalc', int_* atk_rate)
    return ((attrCalc(lv) * atk_rate) / 175) ** 1.25 * 175


def hpCalc(lv):
    str_ = attrCalc(lv)
    current = str_
    for _ in range(lv - 1):
        current = current * hp_lv_rate + hp_add
    hp = hp_base + current
    hp *= hp_rate
    # print('HP', hp)
    return hp


def spellDmdCalc(lv, set_dmg):
    per = attrCalc(lv)
    return set_dmg * attrBaseEnhance(per)


def attrCalc(lv):
    current = attr_base
    for _ in range(lv - 1):
        current = current * (attr_rate) + attr_add
    return current


def defCalc(str_, int_, tend, lv):
    adj = str_ * tend + int_ * (1 - tend)
    def_ = adj * 0.05 + def_base
    # print('defCalc', def_)
    return def_


def damageCalc(lv):
    str_ = int_ = attrCalc(lv)
    dec = 1 + defCalc(str_, int_, 0.5, lv) * def_rate
    dc = atkCalc(lv) / dec
    # print('decreace', 1/dec)
    # print('damageCalc', dc)
    return dc


# 基于属性的技能强化(护盾治疗、法术强度、增益强度)
def attrBaseEnhance(attr):
    adj = 0.0367 * (attr ** 0.845)
    return adj


def critcalTest():
    cri_1 = 1.75
    cri_2 = 2.75
    cri_1_total = 0
    cri_2_total = 0
    for i in range(2333333):

        if random.random() < 0.20:
            cri_1_total += cri_1
            cri_2_total += cri_2
        else:
            cri_1_total += 1
            cri_2_total += 1

    print(cri_1_total, cri_2_total)
    print('%.1f' % (100 * (cri_2_total / cri_1_total)))


def atkToDeathTime(lv):
    return hpCalc(lv) / damageCalc(lv)


# 暴击倍率增益计算
def crit_rate_calc(str_cur, int_cur, defense_str_rate, extra):
    adj = str_cur * defense_str_rate + int_cur * (1 - defense_str_rate)
    return adj / 150 + 1.40 + extra


def dodge_calc(per_cur, extra):
    return 0.05 + extra + per_cur * 0.0009


def recurrence(a_1: float, k: float, m: float, n: int) -> float:
    return (a_1 - m) * k ** (n - 1) + m * ((k ** n - 1) / (k - 1) if k != 1 else n)


if __name__ == '__main__':
    # dm = 100
    # crit_chance = 0.16
    for i in [1, 10, 20, 30]:
        print(attrCalc(i))
        #print(recurrence(attrCalc(i), 1.004, 10, i) + 200 * numerical['hp_rate'])

        # print(crit_rate_calc(attrCalc(i), attrCalc(i), 0.5, 0))
        # a = crit_rate_calc(attrCalc(i), attrCalc(i), 0.5, 0) * crit_chance + \
        # (1 - crit_chance)
        # b = crit_rate_calc(attrCalc(i), attrCalc(i), 0.5, 1.0) * crit_chance + \
        #       (1 - crit_chance)
        #
        # print(a)
        # #print(b)
        # print(b/a)
        # print(f'--------{i}-----------')

        # print(atkCalc(attrCalc(i)))
        # print(damageCalc(i))
        # print(atkToDeathTime(i))
        # defCalc(attrCalc(i),attrCalc(i),0.5,i)
        # damageCalc(i)
    # for i in range(30):
    #     print('spell', spellDmdCalc(i+1,100)/spellDmdCalc(i,100))
    #     print('damage', damageCalc(i+1)/ damageCalc(i))
    #
    # for i in [1,10,20,30]:
    #     print(spellDmdCalc(i,100) / damageCalc(i))
    #     print(spellDmdCalc(i,100))
    # print(damageCalc(30))
