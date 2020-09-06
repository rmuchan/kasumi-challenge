from ksm_challenge_src.attr_calc import _attr_calc, numerical

import seaborn as sns
import matplotlib.pyplot as plt

build_high = 1.232
build_low = 0.825
test_attr_grow = numerical['str_grow'] * 9
compress = numerical['attr_grow_expend']

x = range(1, 31)
y_list = []
for build in ['high', 'mid','low']:
    for edition in ['now', 'new']:
        if build == 'high':
            b = build_high
        elif build == 'low':
            b = build_low
        else:
            b = 1.03

        if edition == 'now':
            color = 'red'
            grow = numerical['str_grow'] * ((b - 1) * numerical['attr_grow_compress'] + 1)
            #grow = numerical['str_grow'] * 0
        else:
            color = 'blue'
            grow = numerical['str_grow'] * ((1 - b) * compress + 1)

        y = [_attr_calc(numerical['str_base'] * b, grow, i) for i in x]

        print(build + edition, y[0], y[14], y[29])
        plt.plot(x, y, label=build + edition, color = color)


plt.legend()
plt.show()

