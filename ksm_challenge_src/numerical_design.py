from random import random
damage = 46
spell_up = 0.16

class testP:
    def __init__(self):
        self.spell = 1.0
        self.total_damage = 0
        self.chance = 0.5

    def do_effect(self):
        self.total_damage += self.do_damage()
        self.spell *= ( 1 + spell_up)

    def do_damage(self):
        return damage * self.spell

    def skill(self):
        self.do_effect()
        while random() < self.chance:
            self.do_effect()
            self.chance *= 0.75


if __name__ == '__main__':
    amount = 1000
    total_damage = 0
    total_spell = 0

    for _ in range(amount):
        a = testP()
        a.skill()
        total_damage += a.total_damage
        total_spell += a.spell

    print(total_damage / amount)
    print(total_spell / amount)