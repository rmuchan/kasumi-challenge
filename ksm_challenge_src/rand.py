import random
from typing import Tuple, Any


def biased(expect: float, min_: float) -> Tuple[float, str]:
    """在指定范围内生成随机数 同时返回评价(SS, S, A, B, C)

    :param expect: 期望值
    :param min_: 允许的最小值
    :return: Tuple (随机值, 评价)
    """
    max_ = expect + (expect - min_) / 7 * 3

    level = [random.random() for _ in range(4)]
    level.sort(reverse=True)
    level = (level[0] + level[1]) / 2

    if level < 0.31:
        appraise = 'C'
    elif level < 0.53:
        appraise = 'B'
    elif level < 0.71:
        appraise = 'A'
    elif level < 0.91:
        appraise = 'S'
    else:
        appraise = 'SS'

    return min_ + level * (max_ - min_), appraise


def cubic(min_: int, max_: int) -> int:
    length = max_ - min_
    y = (1 - random.random()) ** 3
    return round(y * length + min_)


def randomize(template: Any):
    if isinstance(template, list):
        return [randomize(x) for x in template]
    elif isinstance(template, dict):
        mode = template.get('random')
        if mode is None:
            return {k: randomize(v) for k, v in template.items()}
        elif mode == 'choice':
            return randomize(random.choice(template['values']))
        elif mode == 'uniform':
            return random.uniform(template['min'], template['max'])
        elif mode == 'triangular':
            return random.triangular(template['min'], template['max'])
        elif mode == 'triangular_int':
            return round(random.triangular(template['min'] - 0.49, template['max'] + 0.49))
        elif mode == 'cubic':
            return cubic(template['min'], template['max'])
        elif mode == 'biased':
            return biased(template['expect'], template['min'])
        else:
            raise ValueError('Unknown randomize mode')
    else:
        return template
