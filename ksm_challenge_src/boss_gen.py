from .rand import randomize
from .data import data


def boss_gen(template: dict, lv):
    rating = [0, 0]
    boss = randomize(template, rating)

    return boss


if __name__ == '__main__':
    pass



def _recurrence(a_1: float, k: float, m: float, n: int) -> float:
    return (a_1 - m) * k ** (n - 1) + m * (k ** n - 1) / (k - 1)


"""
    "name": "1",
    "is_player": True,
    "attack": 136.14487223446704,
    "defence": 3.615176106521779,
    "HP": 1173.8464482294187,
    "recover_rate": 0.9878750449137164,
    "spell_rate": 0.9223055937285906,
    "buff_rate": 0.960896154525719,
    "crit_rate": 1.75,
    "life_steal_rate": 0,
    "dodge": 0.09289052038201726,
"""