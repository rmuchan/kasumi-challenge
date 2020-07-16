import random


class GameSkill:
    def __init__(self, json_data):
        self.data = json_data
        self.cooldown = 0
        self.last_time = 1

    def can_be_used(self):
        if self.cooldown != 0:
            return False

        if random.random() < self.data['chance'] * self.last_time:
            # 发动了
            self.last_time = 1
            self.cooldown = self.data['cooldown']
            return self.data
        else:
            self.last_time += 1

        return False

    def dec_cooldown(self):
        if self.cooldown > 0:
            self.cooldown -= 1

    @property
    def mp_cost(self):
        return self.data['mp_cost']


if __name__ == '__main__':
    a = GameSkill(dict(chance=0.1, cooldown=5, tp_cost=20))
    total = 0
    for _ in range(233333):
        if a.can_be_used():
            total += 1
        a.dec_cooldown()
    print(total/233333)