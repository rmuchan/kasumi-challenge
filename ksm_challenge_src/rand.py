import heapq
import random
from typing import Tuple, Any, List, Iterable, Callable


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


def randomize(template: Any, rating: List[float] = None):
    if isinstance(template, list):
        return [randomize(x, rating) for x in template]
    elif isinstance(template, dict):
        mode = template.get('random')
        if mode is None:
            return {k: randomize(v, rating) for k, v in template.items()}
        elif mode == 'choice':
            return randomize(random.choice(template['values']), rating)
        elif mode == 'biased':
            return biased(template['expect'], template['min'])

        min_, max_ = template['min'], template['max']
        if mode == 'uniform':
            value = random.uniform(template['min'], template['max'])
        elif mode == 'triangular':
            value = random.triangular(template['min'], template['max'])
        elif mode == 'triangular_int':
            value = round(random.triangular(template['min'] - 0.49, template['max'] + 0.49))
        elif mode == 'cubic':
            value = cubic(template['min'], template['max'])
        else:
            raise ValueError('Unknown randomize mode')

        if rating is not None and 'rating_weight' in template:
            weight = template['rating_weight']
            rating[0] += weight * (value - min_) / (max_ - min_)
            rating[1] += weight
        return value
    else:
        return template


def a_res(population: Iterable[Any], weight_func: Callable[[int, Any], float], count: int):
    """在总体中带权重地不重复选取若干个元素。

    :param population: 总体
    :param weight_func: (下标, 元素) -> 权重
    :param count: 选取的最大数量，当总体数量不足时只会返回等同于总体数量的元素

    :return: 选取的元素列表
    """

    heap = []  # [(new_weight, item), ...]
    for idx, item in enumerate(population):
        wi = weight_func(idx, item)
        ui = random.random()
        ki = ui ** (1 / wi)

        if len(heap) < count:
            heapq.heappush(heap, (ki, item))
        elif ki > heap[0][0]:
            heapq.heappush(heap, (ki, item))

            if len(heap) > count:
                heapq.heappop(heap)

    return [item[1] for item in heap]
