import json

from ksm_challenge_src import util
# from .data import data
#
# numerical = data.numerical
#
#
# # 经验获取计算  ————  利用这个计算某个等级的boss的经验平均应该有多少
# def exp_earn_calc(lv: int):
#     current = numerical['exp_earn_base']
#     for i in range(lv - 1):
#         current = current * numerical['exp_earn_rate'] + numerical['exp_earn_add']
#     return current
#
#
#
# def res_print(func):
#     def wrapper(arg):
#         value = func(arg)
#         print(value)
#         return value
#
#     return wrapper
from ksm_challenge_src.GameChar import numerical
import matplotlib.pyplot as plt


def _exp_requirement(lv: int) -> 100:
    return int(
        util.recurrence(numerical['exp_base'], numerical['exp_add_rate'], numerical['exp_add_point'], lv) / 100) * 100


def exp_to_talent_coin(exp):
    return int(i ** numerical['talent_coin_earn_index'] * numerical['talent_coin_earn_rate'])

if __name__ == '__main__':

    a = []
    for i in range(1, 31):
        a.append(_exp_requirement(i))


    a = [int(i ** numerical['talent_coin_earn_index'] * numerical['talent_coin_earn_rate']) for i in a]

    with open('data/talent.json') as FILE:
        talent = json.load(FILE)

    param = talent['talent_coin_earn_rate']
    b = []
    for lvl in range(param['max_level']):
        b.append(1 * util.recurrence(param['cost_base'], param['cost_ratio'], param['cost_grow'], lvl + 1))


    plt.plot(range(1,31), a)
    plt.plot(range(param['max_level']), b)
    plt.show()