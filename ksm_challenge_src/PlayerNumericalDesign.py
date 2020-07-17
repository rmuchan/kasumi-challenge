from .data import data

numerical = data.numerical

lv_list = range(1, 31)

exp_list_1 = [1000, 1300, 1600, 2000, 2600, 3200, 3900, 4800, 5900, 7200, 8700, 10600, 12800, 15500, 18700, 22600,
              27200, 32700, 39400, 47400, 57000, 68500, 82300, 98800, 118700, 142500, 171200, 205500, 246700, 296200]
exp_overlay_1 = [0, 1000, 2300, 3900, 5900, 8500, 11700, 15600, 20400, 26300, 33500, 42200, 52800, 65600, 81100, 99800,
                 122400, 149600, 182300, 221700, 269100, 326100, 394600, 476900, 575700, 694400, 836900, 1008100,
                 1213600, 1460300, 1756500]

exp_earn = []



# 生成每级升级需要的EXP
def exp_requirement(lvs: int):
    current = numerical['exp_base']
    for i in range(lvs - 1):
        current = current * numerical['exp_add_rate'] + numerical['exp_add_point']
    return current


# 生成经验数组
def exp_overlay_gen() -> list:
    exp_list = []
    for i in range(1, 31):
        exp_list.append(int(exp_requirement(i) / 100) * 100)
    exp_overlay = [0]
    for i in exp_list:
        exp_overlay.append(exp_overlay[-1] + i)
    return exp_overlay


# 根据经验等级计算
def lv_calc(exp, int):
    for i in range(1, 30):
        if exp_overlay_1[i - 1] <= exp < exp_overlay_1[i]:
            return i
    return 30


# 经验获取计算  ————  利用这个计算某个等级的boss的经验平均应该有多少
def exp_earn_calc(lv: int):
    current = numerical['exp_earn_base']
    for i in range(lv - 1):
        current = current * numerical['exp_earn_rate'] + numerical['exp_earn_add']
    return current


def res_print(func):
    def wrapper(arg):
        value = func(arg)
        # print(value)
        return value

    return wrapper


if __name__ == '__main__':
    print(exp_overlay_gen())
