import os, json
from .rand import biased
import random
from typing import Tuple, Any

# 读数值配置文件  路径可能会修改
with open('%s/%s' % (os.path.dirname(__file__), 'chara-numerical.json')) as File:
    chara_numerical = json.load(File)


## 以下到类声明之前的所有函数都会用于战斗直接相关的属性的生成，在类中无需记录基础三属性 ----


# 属性计算
def attr_calc(attr_base, attr_grow, lv):
    current = attr_base
    for _ in range(lv-1):
        current = current*(chara_numerical['attr_rate']) + attr_grow
    return current

# 攻击计算
def atk_calc(int_cur):
    return int_cur * chara_numerical['atk_rate']


# 血量计算  -  modify基本上就是给Shadoul用的了(
def hp_calc(str_cur, life_base, life_grow, lv, modify):
    current = str_cur
    for _ in range(lv-1):
        current = current * chara_numerical['hp_lv_rate'] + life_grow
    hp = life_base + current
    hp *= chara_numerical['hp_rate'] * modify
    return hp


# 防御计算
def def_calc(str_cur, int_cur, defense_str_rate, def_base, extra):
    adj = str_cur * defense_str_rate + int_cur * (1 - defense_str_rate)
    return adj * chara_numerical['def_adj_rate'] + def_base + extra


# 暴击率增益计算
def crit_rate_calc(str_cur, int_cur, defense_str_rate, def_base, extra):
    adj = str_cur * defense_str_rate + int_cur * (1 - defense_str_rate)
    return adj * chara_numerical['def_adj_rate'] + def_base + extra


# 下面会有三个基于属性的技能强化率的计算会用到这个函数
def attr_based_enhance(attr):
    return chara_numerical['enhance_constant'] * (attr ** chara_numerical['enhance_exponent'])


# 护盾与治疗倍率
def recover_rate_calc(per_cur, str_cur, health_per_rate):
    return attr_based_enhance(per_cur * health_per_rate + str_cur * (1 - health_per_rate))


# 魔法伤害增强 - 对于Magecian种族，mage_rate会有更高的数值
def spell_rate_calc(int_cur, per_cur, magic_int_rate, extra):
    return attr_based_enhance(int_cur * magic_int_rate + per_cur * (1 - magic_int_rate)) * extra


# 增益类技能效果增强
def buff_rate_calc(per_cur):
    return attr_based_enhance(per_cur)


# 闪避
def dodge_calc(per_cur, extra):
    return chara_numerical['dodge_base'] + extra + per_cur * chara_numerical['dodge_rate']

chara = dict(str_cur=50,
             int_cur=50,
             per_cur=50,
             defense_str_rate=0.5,
             magic_int_rate=0.5,
             health_per_rate=0.5,
             life_base = 200,
             life_grow = 5,
             HP = 200,
             defence = 3,
             attack = 80
             )


class GameChara:
    def __init__(self, chara: dict):
        self.attributes = chara
        self.HP = chara['HP']
        self.shield = 0

    @property
    def defence(self):
        return self.attributes['defence']

    @property
    def attack(self):
        return self.attributes['attack']

    @property
    def crit_rate(self):
        return self.attributes['crit_rate']

    @property
    def recover_rate(self):
        return self.attributes['recover_rate']

    @property
    def buff_rate(self):
        return self.attributes['buff_rate']

    @property
    def spell_rate(self):
        return self.attributes['spell_rate']

    @property
    def is_dead(self):
        return self.HP <= 0

    """
    角色物理攻击。
    本次伤害会有一个随机的波动，且会有暴击的可能
    返回值为一个tuple，[0]为已算入暴击伤害的攻击伤害，[1]为是否暴击
    """
    def do_attack(self) -> Tuple[float, bool]:
        attack_damage = biased(1, 0.7) * self.attack
        # 暴击判断
        is_crit = (random.random() < chara_numerical['crit_chance'])

        if is_crit:
            attack_damage *= self.crit_rate

        return attack_damage, is_crit

    """
    角色受到伤害，需要传入伤害量，可选是否为法术伤害。
    伤害会优先对护盾造成伤害，溢出的伤害仍然会作用在本体
    返回一个tuple，[0]为实际伤害量，[1]为击破护盾状态(0: 直接伤害, 1: 护盾被击破, 2: 护盾未击破)
    """
    def take_damage(self, damage, magic=False):

        shield_break = 0
        shield_damage = 0

        # 护盾将会被优先攻击
        if self.shield > 0:
            shield_break = 1
            shield_damage = self._shield_hurt(damage)
            damage -= shield_damage
            # 伤害全部被护盾挡下
            if damage == 0:
                return shield_damage, 2

        if magic:
            real_damage = self._life_hurt(damage)
        else:
            real_damage = self._life_hurt(self._damage_reduce(damage))

        return real_damage+shield_damage, shield_break

    """
    角色的护盾受到攻击，需要传入伤害量
    如果护盾未击破，返回伤害量
    否则返回护盾量
    """
    def _shield_hurt(self, damage):
        if damage < self.shield:
            self.shield -= damage
            return damage
        else:
            shield = self.shield
            self.shield = 0
            return shield

    """
    角色扣血时，需要传入伤害量。
    返回实际造成的伤害
    """
    def _life_hurt(self, damage):
        self.HP -= damage
        return damage

    """
    计算护甲伤害减免，传入伤害量。
    返回护甲减免后的伤害值
    """
    def _damage_reduce(self, damage):
        damage_decrease = 1 + chara_numerical['def_rate'] * self.defence
        return damage / damage_decrease

    """
    生命恢复。传入恢复量
    超过最大值的将会被舍弃
    返回实际恢复量
    """
    def _recover(self, recovery):
        self.HP += recovery
        if self.HP <= self.attributes['HP']:
            return recovery
        else:
            diff = self.HP - self.attributes['HP']
            self.HP = self.attributes['HP']
            return diff


if __name__ == '__main__':
    a = GameChara(chara)
    #print(crit_rate_calc())
