import random
from typing import Tuple, List, Optional

from .GameSkill import GameSkill
from .data import data
from .rand import biased

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

    # ————————————————————————————
    #           属性信息
    # ————————————————————————————

    @property
    def defence(self):
        add = 0
        if 'defence' in self.buff.keys():
            for item in self.buff['defence']:
                add += item[0]
        return self.attributes['defence'] + add

    @property
    def name(self):
        return self.attributes['name']

    @property
    def not_short_hp(self):
        return self.attributes['not_short_hp']

    @property
    def attack(self):
        add = 0
        if 'attack_add' in self.buff.keys():
            for item in self.buff['attack_add']:
                add += item[0]
        return self.attributes['attack'] + add

    # 暴击率是非线性叠加
    @property
    def crit_chance(self):
        not_crit_chance = 1
        if 'crit_chance' in self.buff.keys():
            for item in self.buff['crit_chance']:
                not_crit_chance *= (1 - item[0])
        return 1 - (1 - self.attributes['crit_chance']) * not_crit_chance

    @property
    def crit_rate(self):
        add = 0
        if 'crit_rate' in self.buff.keys():
            for item in self.buff['crit_rate']:
                add += item[0]
        return self.attributes['crit_rate'] + add

    @property
    def dodge(self):
        add = 0
        if 'dodge' in self.buff.keys():
            for item in self.buff['dodge']:
                add += item[0]
        return self.attributes['dodge'] + add

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
        enhance = 1
        if 'spell_enhance' in self.buff.keys():
            for item in self.buff['spell_enhance']:
                enhance *= (item[0] + 1)
        return self.attributes['spell_rate'] * enhance

    @property
    def not_dead(self):
        return self.HP > 0

    @property
    def normal_attack(self):
        return self.attributes['normal_attack']

    @property
    def is_silence(self):
        if 'silence' in self.buff.keys():
            return True
        else:
            return False

    # ————————————————————————————
    #           战斗功能
    # ————————————————————————————

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
        返回一个tuple，[0]为实际伤害量，[1]为攻击状态(-1: 闪避了, 0: 直接伤害, 1: 护盾被击破, 2: 护盾未击破)
        """
        shield_break = 0
        shield_damage = 0

        # 考虑闪避
        if random.random() < self.dodge and not magic:
            return 0, -1

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

    def buff_fade(self):
        """
        回合结束时调用。
        移除所有持续时间为0的buff，其余所有buff持续时间-1
        """
        for buff_type in self.buff:
            self.buff[buff_type] = [(i[0], i[1] - 1) for i in self.buff[buff_type] if i[1] > 0]

        self.buff = {k: v for k, v in self.buff.items() if v}

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
        if self.is_silence:
            return [self.normal_attack]

        if self.MP >= 1000:
            self.MP = 0
            return [self.attributes['unique']]
        for i in range(3):
            ret = self.skills[i].can_be_used()
            if ret:
                if self.MP < ret['mp_cost']:
                    return [self.normal_attack]
                self.MP -= ret['mp_cost']
                return [ret]

        return [self.normal_attack]

    def turn_mp_gain(self):
        """
        每回合固定获取一定的MP
        """
        self.gain_mp(random.random() * numerical['random_mp_gain_extra'] + numerical['random_mp_gain_base'])

    def life_display(self) -> str:
        """
        这个函数将会返回一个图形化的体力条
        """
        hp_bar = ''
        adj_hp = self.HP if self.not_short_hp else int(self.HP / numerical['boss_display_shorten'])
        whole = int(adj_hp / numerical['hp_display_unit'])
        rest = adj_hp - numerical['hp_display_unit'] * whole

        hp_bar += '▉' * whole
        hp_bar += hp_block(rest)

        return hp_bar

    def mp_display(self) -> str:
        value = int(self.MP / (1000 / 7))
        return mp_block_list[value]

    # ————————————————————————————
    #         技能效果执行
    # ————————————————————————————

    def use_effect(self, selector: List['GameChar'], effect: dict) -> Optional[list]:
        """
        角色行动时一定会调用这个函数，发动技能效果。
        :param selector: 选择到的角色数组
        :param effect: 技能的dict信息
        :return: {角色名: {feedback: 返回信息, param: {返回信息需要用到的参数}}}
        """
        if len(selector) == 0:
            return None

        param = effect['param']

        ret = []

        # 普通攻击
        if effect['type'] == 'NORMAL_ATK':
            for obj in selector:
                atk_damage, is_crit = self.do_attack()
                real_damage, atk_status = obj.take_damage(atk_damage)
                # 吸血
                self.recover(real_damage)

                # miss
                if atk_status == -1:
                    ret.append({
                        'feedback': '{target}闪避了攻击',
                        'merge_key': {'target': self._self_replace(obj.name)},
                        'param': {}
                    })
                else:
                    feedback = ''
                    if is_crit:
                        feedback += '暴击！'
                    feedback += '对{target}'
                    # 未击破
                    if atk_status == 2:
                        feedback += '的护盾'

                    feedback += '造成了{amount:.0f}点伤害'
                    # 击破护盾了
                    if atk_status == 1:
                        feedback += '，破坏了护盾'
                    ret.append({
                        'feedback': feedback,
                        'merge_key': {'target': self._self_replace(obj.name)},
                        'param': {'amount': real_damage}
                    })

        # 魔法伤害
        elif effect['type'] == 'MGC_DMG':
            for obj in selector:
                magic_damage = param[0][0] * self.spell_rate
                real_damage, atk_status = obj.take_damage(magic_damage, magic=True)
                feedback = '对{target}'
                if atk_status == 2:
                    feedback += '的护盾'
                feedback += '造成了{amount:.0f}点魔法伤害'
                if atk_status == 1:
                    feedback += '，破坏了护盾'
                ret.append({
                    'feedback': feedback,
                    'merge_key': {'target': self._self_replace(obj.name)},
                    'param': {'amount': real_damage}
                })

        # 固定值攻击强化
        elif effect['type'] == 'PHY_ATK_BUFF_CONST':
            for obj in selector:
                real_added = obj._add_attack_buff(param[0][0], param[1])
                ret.append({
                    'feedback': '强化了{target}{amount:.0f}点攻击，持续{duration}回合',
                    'merge_key': {'target': self._self_replace(obj.name), 'duration': param[1]},
                    'param': {'amount': real_added}
                })

        # 百分比强化
        elif effect['type'] == 'PHY_ATK_BUFF_RATE':
            for obj in selector:
                real_point = obj._attack_buff(param[0][0])
                real_added = obj._add_attack_buff(real_point, param[1])
                ret.append({
                    'feedback': '强化了{target}{amount:.0f}点攻击，持续{duration}回合',
                    'merge_key': {'target': self._self_replace(obj.name), 'duration': param[1]},
                    'param': {'amount': real_added}
                })

        # 治疗
        elif effect['type'] == 'HEAL':
            for obj in selector:
                real_heal = obj.recover(param[0][0])
                ret.append({
                    'feedback': '恢复了{target}{heal:.0f}点生命',
                    'merge_key': {'target': self._self_replace(obj.name)},
                    'param': {'heal': real_heal}
                })

        # 护盾
        elif effect['type'] == 'SHIELD':
            for obj in selector:
                real_shield = obj.give_shield(param[0][0])
                if real_shield == 0:
                    feedback = '{target}当前的护盾更好！没有使用新的护盾'
                else:
                    feedback = '为{target}添加了{shield:.0f}点护盾'
                ret.append({
                    'feedback': feedback,
                    'merge_key': {'target': self._self_replace(obj.name)},
                    'param': {'shield': real_shield}
                })

        # 沉默
        elif effect['type'] == 'SILENCE':
            for obj in selector:
                obj._add_silence_buff(param[1])
                ret.append({
                    'feedback': '沉默{target}{duration}回合',
                    'merge_key': {'target': self._self_replace(obj.name), 'duration': param[1]},
                    'param': {}
                })

        # 净化
        elif effect['type'] == 'PURIFY':
            for obj in selector:
                obj._purify()
                ret.append({
                    'feedback': '清除了{target}所有的状态',
                    'merge_key': {'target': self._self_replace(obj.name)},
                    'param': {}
                })

        # 攻击削弱
        elif effect['type'] == 'ATK_DEBUFF':
            for obj in selector:
                oppo_to_decrease_atk_point = obj._attack_buff(param[0][0]) * self.buff_rate
                real_minus = obj._add_attack_buff(oppo_to_decrease_atk_point, param[1], is_debuff=True)
                ret.append({
                    'feedback': '削弱了{target}{minus_value:.0f}点攻击，持续{duration}回合',
                    'merge_key': {'target': self._self_replace(obj.name), 'duration': param[1]},
                    'param': {'minus_value': real_minus}
                })

        # 法术增强
        elif effect['type'] == 'MGC_BUFF_RATE':
            for obj in selector:
                real_added = obj._add_spell_buff(param[0][0], param[1])
                ret.append({
                    'feedback': '强化了{target}{amount:.0%}的法术强度，持续{duration}回合',
                    'merge_key': {'target': self._self_replace(obj.name), 'duration': param[1]},
                    'param': {'amount': real_added}
                })

        # 护甲衰减
        elif effect['type'] == 'DEF_DEC':
            for obj in selector:
                real_added = obj._add_defence_buff(param[0][0] * self.buff_rate, param[1], is_debuff=True)
                ret.append({
                    'feedback': '削弱了{target}{amount:.1f}点防御，持续{duration}回合',
                    'merge_key': {'target': self._self_replace(obj.name), 'duration': param[1]},
                    'param': {'amount': real_added}
                })

        # 暴击伤害倍率提升
        elif effect['type'] == 'CRIT_RATE_BUFF':
            for obj in selector:
                real_added = obj._add_crit_rate(param[0][0], param[1])
                ret.append({
                    'feedback': '提升了{target}{amount:.0%}的暴击伤害倍率，持续{duration}回合',
                    'merge_key': {'target': self._self_replace(obj.name), 'duration': param[1]},
                    'param': {'amount': real_added}
                })

        # 暴击率提升
        elif effect['type'] == 'CRIT_CHANCE_BUFF':
            for obj in selector:
                real_added = obj._add_crit_chance(param[0][0], param[1])
                ret.append({
                    'feedback': '提升了{target}{amount:.1f}的暴击率，持续{duration}回合',
                    'merge_key': {'target': self._self_replace(obj.name), 'duration': param[1]},
                    'param': {'amount': real_added}
                })

        # 闪避率提升
        elif effect['type'] == 'DODGE_BUFF':
            for obj in selector:
                real_added = obj._add_dodge_buff(param[0][0], param[1])
                ret.append({
                    'feedback': '提升了{target}{amount:.0%}的闪避率，持续{duration}回合',
                    'merge_key': {'target': self._self_replace(obj.name), 'duration': param[1]},
                    'param': {'amount': real_added}
                })

        else:
            raise ValueError('出现了未知的效果类型')
        return ret

    # ————————————————————————————
    #           效果处理
    # ————————————————————————————

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

    def recover(self, recovery):
        """
        生命恢复。传入恢复量
        超过最大值的将会被舍弃
        返回实际恢复量
        """
        self.HP += recovery * self.recover_rate
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
        value *= self.recover_rate
        if self.shield >= value:
            return 0
        else:
            diff = value - self.shield
            self.shield = value
            return diff

    def gain_mp(self, value):
        """
        MP增加的时候使用，函数会保证MP值不超过1000点
        """
        self.MP += value
        if self.MP > 1000:
            self.MP = 1000

    def _add_attack_buff(self, value, time, is_debuff=False):
        """
        给角色添加一个攻击力的buff
        这个buff会受到角色本身的buff_rate的加成
        is_debuff为真时，此时的效果不会受到作用目标的buff_rate的加成，同时自动帮助玩家变为负数添加buff中
        time为持续回合数
        返回实际强化量
        """
        if is_debuff:
            real_point = -value
        else:
            real_point = value * self.buff_rate
        self._add_buff('attack_add', real_point, time)
        return abs(real_point)

    def _add_silence_buff(self, time):
        self._add_buff('silence', True, time)

    def _add_defence_buff(self, value, time, is_debuff=False):
        """
        为角色添加防御相关的buff
        :param value: buff的效果量
        :param time: 持续回合数
        :param is_debuff: 是否为Debuff，如果是debuff，数值将会自动反过来，并且不会被自身的buff_rate强化
        :return: 实际衰减量
        """
        if is_debuff:
            real_point = -value
        else:
            real_point = value * self.buff_rate
        self._add_buff('defence', real_point, time)
        return abs(real_point)

    def _add_spell_buff(self, value, time, is_debuff=False):
        """
        添加一个魔法伤害提升的buff
        这个buff不会会受到角色本身的buff_rate的加成 (主要是考虑到强度问题，后期会很爆炸()
        is_debuff为真时，此时的效果不会受到作用目标的buff_rate的加成，同时自动帮助玩家变为负数添加buff中
        time为持续回合数
        返回实际强化率(为百分号形式)
        """
        if is_debuff:
            real_rate = -value
        else:
            real_rate = value
        self._add_buff('spell_enhance', real_rate, time)
        return abs(real_rate)

    def _add_crit_chance(self, value, time, is_debuff=False):
        """
        添加暴击率提升的buff
        不吃buff_rate加成
        is_debuff为真时，自动帮助玩家变为负数添加buff中
        time为持续回合数
        返回实际强化/弱化率
        """
        if is_debuff:
            real_rate = -value
        else:
            real_rate = value
        self._add_buff('crit_chance', real_rate, time)
        return abs(real_rate)

    def _add_crit_rate(self, value, time, is_debuff=False):
        """
        添加暴击伤害倍率提升的buff
        受到buff_rate的加成
        is_debuff为真时，不会受到作用目标的buff_rate的加成，且自动帮助玩家变为负数添加buff中
        time为持续回合数
        返回实际强化/弱化率
        """
        if is_debuff:
            real_rate = -value
        else:
            real_rate = value * self.buff_rate
        self._add_buff('crit_rate', real_rate, time)
        return abs(real_rate)

    def _add_dodge_buff(self, value, time, is_debuff=False):
        """
        添加闪避的buff
        不吃buff_rate加成
        is_debuff为真时，自动帮助玩家变为负数添加buff中
        time为持续回合数
        返回实际强化/弱化率
        """
        if is_debuff:
            real_rate = -value
        else:
            real_rate = value
        self._add_buff('dodge', real_rate, time)
        return abs(real_rate)

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
        最小伤害为1
        """
        if damage <= 0:
            damage = 1
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

    def _purify(self):
        self.buff = {}

    def _self_replace(self, chara_name: str) -> str:
        if chara_name == self.name:
            return '自身'
        return f'[{chara_name}]'

    def __repr__(self):
        S = self.name + ', '
        S += '%.0f/%.0f, ' % (self.HP, self.attributes['HP'])
        S += 'shield: %.0f' % self.shield
        S += 'buff: %s' % str(self.buff)
        return S

hp_block_list = '▏▎▍▌▋▊▉'
mp_block_list = '▁▂▃▄▅▆▇♠'


def hp_block(value):
    value = int(value / (numerical['hp_display_unit'] / 7))
    return hp_block_list[value]


def life_display(hp) -> str:
    hp_bar = ''

    whole = int(hp / numerical['hp_display_unit'])
    rest = hp - numerical['hp_display_unit'] * whole

    hp_bar += '▉' * whole
    hp_bar += hp_block(rest)

    return hp_bar


if __name__ == '__main__':
    pass
