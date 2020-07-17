import matplotlib.pyplot as plt
import data

numerical = data.numerical


# 经验获取计算  ————  利用这个计算某个等级的boss的经验平均应该有多少
def exp_earn_calc(lv: int):
    current = numerical['exp_earn_base']
    for i in range(lv - 1):
        current = current * numerical['exp_earn_rate'] + numerical['exp_earn_add']
    return current



def res_print(func):
    def wrapper(arg):
        value = func(arg)
        print(value)
        return value

    return wrapper



if __name__ == '__main__':
    pass