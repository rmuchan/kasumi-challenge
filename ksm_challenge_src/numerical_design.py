from ksm_challenge_src.attr_calc import attr_calc, numerical

import seaborn as sns
import matplotlib.pyplot as plt

# 暴击倍率增益计算
def crit_rate_calc(str_cur, extra):
    return str_cur * numerical['crit_int_convert_rate'] + 0.22 + extra

def c_new(str_cur, extra):
    return str_cur * 0.0036 + 0.20 + extra

def damge_p(chance, rate):
    return chance * rate + 1 - chance

if __name__ == '__main__':
    for attr in [120]:
        print('旧：' + str(attr), end='    ')
        a1 = crit_rate_calc(attr, 0) + 1
        print(a1)
        print(damge_p(0.11, a1))
        print('新：'+ str(attr), end='    ')
        a2 = c_new(attr, 0) + 1
        print(a2)
        print(damge_p(0.21, a2))