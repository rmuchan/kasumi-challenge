import random
from typing import Tuple, List, Optional

import data
from GameSkill import GameSkill
from rand import biased

numerical = data.numerical


class GameChar:
    def __init__(self, chara: dict):
        self.attributes = chara
        self.HP = chara['HP']
        self.shield = 0
        self.buff = {}
        self.MP = 0
        self.skills = []
        for i in range(3):
            self.skills.append(GameSkill(self.attributes[f'skill_{i + 1}']))

    @property
    def defence(self):
        return self.attributes['defence']

    @property
    def name(self):
        return  self.attributes['name']

    @property
    def attack(self):
        add = 0
        if 'attack_add' in self.buff.keys():
            for item in self.buff['attack_add']:
                add += item[0]
        return self.attributes['attack'] + add

    @property
    def crit_chance(self):
        return numerical['crit_chance']

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
    def hp_percentage(self):
        return self.HP / self.attributes['HP']

    @property
    def spell_rate(self):
        return self.attributes['spell_rate']

    @property
    def not_dead(self):
        return self.HP > 0

    @property
    def normal_attack(self):
        return self.attributes['normal_attack']

    def do_attack(self) -> Tuple[float, bool]:
        """
        角色物理攻击。
        本次伤害会有一个随机的波动，且会有暴击的可能
        返回值为一个tuple，[0]为已算入暴击伤害的攻击伤害，[1]为是否暴击
        """
        attack_damage = biased(1, numerical['damage_fluctuation'])[0] * self.attack
        # 暴击判断
        is_crit = (random.random() < self.crit_chance)

        if is_crit:
            attack_damage *= self.crit_rate

        return attack_damage, is_crit

    def take_damage(self, damage, magic=False):
        """
        角色受到伤害，需要传入伤害量，可选是否为法术伤害。
        伤害会优先对护盾造成伤害，溢出的伤害仍然会作用在本体
        返回一个tuple，[0]为实际伤害量，[1]为击破护盾状态(0: 直接伤害, 1: 护盾被击破, 2: 护盾未击破)
        """
        shield_break = 0
        shield_damage = 0

        # 护盾将会被优先攻击
        if self.shield > 0:
            shield_break = 1
            total_damage = damage
            damage = self._shield_hurt(damage)
            # 伤害全部被护盾挡下
            if damage == 0:
                return total_damage - damage, 2

        if magic:
            real_damage = self._life_hurt(damage)
        else:
            real_damage = self._life_hurt(self._damage_reduce(damage))

        return real_damage + shield_damage, shield_break

    def recover(self, recovery):
        """
        生命恢复。传入恢复量
        超过最大值的将会被舍弃
        返回实际恢复量
        """
        self.HP += recovery
        if self.HP <= self.attributes['HP']:
            return recovery
        else:
            diff = self.HP - self.attributes['HP']
            self.HP = self.attributes['HP']
            return diff

    def give_shield(self, value):
        """
        添加护盾时使用，传入护盾量
        护盾不会叠加，只会取最大值
        返回实际护盾添加量
        """
        if self.shield >= value:
            return 0
        else:
            diff = value - self.shield
            self.shield = value
            return diff

    def add_attack_buff(self, value, time):
        """
        给角色添加一个攻击力的buff
        这个buff会受到角色本身的buff_rate的加成
        当value为负数的时候则为攻击力降低
        time为持续回合数
        返回实际强化量
        """
        real_point = value * self.buff_rate
        self._add_buff('attack_add', real_point, time)
        return real_point

    def buff_fade(self):
        """
        回合结束时调用。
        移除所有持续时间为0的buff，其余所有buff持续时间-1
        """
        for buff_type in self.buff:
            self.buff[buff_type] = [(i[0], i[1] - 1) for i in self.buff[buff_type] if i[1] > 0]

    def skill_cooldown(self):
        """
        减全部技能的CD
        """
        for skill in self.skills:
            skill.dec_cooldown()

    def skill_activate(self):
        """
        发动技能。顺序依次为终极技能，技能123，最后普通攻击作为一个技能
        :return: 技能的dict模板
        """
        if self.MP >= 1000:
            self.MP = 0
            return self.attributes['unique']
        for i in range(3):
            ret = self.skills[i].can_be_used()
            if ret:
                if self.MP < ret['mp_cost']:
                    return self.normal_attack
                self.MP -= ret['mp_cost']
                return ret

        return self.normal_attack

    def turn_mp_gain(self):
        """
        每回合固定获取一定的MP
        """
        self.gain_mp(random.random() * numerical['random_mp_gain_extra'] + numerical['random_mp_gain_base'])

    def gain_mp(self, value):
        """
        MP增加的时候使用，函数会保证MP值不超过1000点
        """
        self.MP += value
        if self.MP > 1000:
            self.MP = 1000

    # TODO 技能效果执行
    def use_effect(self, selector: List['GameChar'], effect: dict) -> Optional[dict]:
        """
        角色行动时一定会调用这个函数，发动技能效果。
        :param selector: 选择到的角色数组
        :param effect: 技能的dict信息
        :return: {角色名: {feedback: 返回信息, param: {返回信息需要用到的参数}}}
        """
        if len(selector) == 0:
            return None

        param = effect['param']

        ret = {}

        # 普通攻击
        if effect['type'] == 'NORMAL_ATK':
            for obj in selector:
                atk_damage, is_crit = self.do_attack()
                real_damage, shield_status = obj.take_damage(atk_damage)
                tgt = self._self_replace(obj.name)
                feedback = ''
                if is_crit:
                    feedback += '暴击！'
                feedback += '对{target}'
                # 未击破
                if shield_status == 2:
                    feedback += '的护盾'

                feedback += '造成了{damage:.0f}点伤害'
                # 击破护盾了
                if shield_status == 1:
                    feedback += '，破坏了护盾'
                ret[tgt] = {
                    'feedback': feedback,
                    'param': {'damage': real_damage}
                }

        # 魔法伤害
        elif effect['type'] == 'MGC_DMG':
            for obj in selector:
                magic_damage = param[0][0] * self.spell_rate
                real_damage, _ = obj.take_damage(magic_damage, magic=True)
                tgt = self._self_replace(obj.name)
                if tgt in ret:
                    ret[tgt]['param']['damage'] += real_damage
                else:
                    ret[tgt] = {
                        'feedback': '对{target}造成了{damage:.0f}点魔法伤害',
                        'param': {'damage': real_damage}
                    }

        # 固定值攻击强化
        elif effect['type'] == 'PHY_ATK_BUFF_CONST':
            for obj in selector:
                real_added = obj.add_attack_buff(param[0][0], param[1])
                tgt = self._self_replace(obj.name)
                if tgt in ret:
                    ret[tgt]['param']['point'] += real_added
                else:
                    ret[tgt] = {
                        'feedback': '强化了{target}{point:.0f}点攻击，持续{duration}回合',
                        'param': {'point': real_added, 'duration': param[1]}
                    }

        # 百分比强化
        elif effect['type'] == 'PHY_ATK_BUFF_RATE':
            for obj in selector:
                real_point = obj._attack_buff(param[0][0])
                real_added = obj.add_attack_buff(real_point, param[1])
                tgt = self._self_replace(obj.name)
                if tgt in ret:
                    ret[tgt]['param']['point'] += real_added
                else:
                    ret[tgt] = {
                        'feedback': '强化了{target}{point:.0f}点攻击，持续{duration}回合',
                        'param': {'point': real_added, 'duration': param[1]}
                    }

        return ret


    def _shield_hurt(self, damage):
        """
        角色的护盾受到攻击，需要传入伤害量
        如果护盾未击破，返回0
        否则返回溢出的伤害量
        """
        if damage < self.shield:
            self.shield -= damage
            return 0
        else:
            damage -= self.shield
            self.shield = 0
            return damage

    def _life_hurt(self, damage):
        """
        角色扣血时，需要传入伤害量。
        返回实际造成的伤害，同时增加TP值
        """
        self.HP -= damage
        damage_percent = damage / self.attributes['HP']
        self.gain_mp(damage_percent * 1000)
        return damage

    def _damage_reduce(self, damage):
        """
        计算护甲伤害减免，传入伤害量。
        返回护甲减免后的伤害值
        """
        damage_decrease = 1 + numerical['def_rate'] * self.defence
        return damage / damage_decrease

    def _attack_buff(self, rate):
        """
        如果一个技能涉及到百分比强化攻击力，调用这个函数，传入提升量。
        返回实际战斗力提升点数
        """
        return self.attributes['attack'] * rate

    def _add_buff(self, buff_type, value, time):
        """
        用作一个添加和管理buff的统一函数接口
        :param buff_type: buff的类型，具体请查阅文档
        :param value: buff的数值
        :param time: 持续时间
        """
        if buff_type not in self.buff:
            self.buff[buff_type] = []

        self.buff[buff_type].append((value, time))

    def _self_replace(self, chara_name: str) -> str:
        if chara_name == self.name:
            return '自身'
        return chara_name

if __name__ == '__main__':
    pass
    # print(crit_rate_calc())
