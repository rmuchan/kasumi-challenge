import random
from typing import Tuple, List, Optional

from .GameSkill import GameSkill
from .data import data
from .rand import biased

numerical = data.numerical


class NoTargetSelected(RuntimeError):
    pass


class GameChar:
    def __init__(self, chara: dict, name: str):
        self.attributes = chara
        self.name = name
        self.HP = chara['HP']
        self.shield = 0
        self.buff = {}
        self.MP = 0
        self.skills = []
        for i in range(3):
            self.skills.append(GameSkill(self.attributes[f'skill_{i + 1}']))
        self.turn_mp_gain()

    # ————————————————————————————
    #           属性信息
    # ————————————————————————————

    @property
    def defence(self):
        return max(self.attributes['defence'] + self.buff_calc('defence_enhanced') - self.buff_calc('defence_weaken'),
                   1)

    @property
    def not_short_hp(self):
        return self.attributes['not_short_hp']

    @property
    def attack(self):
        return max(
            (self.attributes['attack'] + self.buff_calc('attack_enhanced')) * self.buff_calc_spec('attack_weaken'), 1)

    # 暴击率是非线性叠加
    @property
    def crit_chance(self):
        not_crit_chance = 1
        if 'crit_chance_enhanced' in self.buff.keys():
            for item in self.buff['crit_chance_enhanced']:
                not_crit_chance *= (1 - item[0])
        return 1 - (1 - self.attributes['crit_chance']) * not_crit_chance

    @property
    def crit_rate(self):
        return self.attributes['crit_rate'] + self.buff_calc('crit_rate_enhanced')

    @property
    def dodge(self):
        return self.attributes['dodge'] + self.buff_calc('dodge_enhanced')

    @property
    def life_steal_rate(self):
        return self.attributes['life_steal_rate'] + self.buff_calc('life_steal_enhanced')

    @property
    def recover_rate(self):
        return self.attributes['recover_rate'] * self.buff_calc('recover_rate_enhanced',
                                                                is_multi=True) * self.buff_calc_spec(
            'recover_rate_weaken')

    @property
    def buff_rate(self):
        return self.attributes['buff_rate'] * self.buff_calc('buff_rate_enhanced', is_multi=True) * self.buff_calc_spec(
            'buff_rate_weaken')

    @property
    def hp_percentage(self):
        return self.HP / self.attributes['HP']

    @property
    def spell_rate(self):
        return self.attributes['spell_rate'] * self.buff_calc('spell_rate_enhanced',
                                                              is_multi=True) * self.buff_calc_spec(
            'spell_rate_weaken')

    @property
    def not_dead(self):
        return self.HP > 0

    @property
    def normal_attack(self):
        return self.attributes['normal_attack']

    @property
    def is_silence(self):
        return 'silence' in self.buff.keys()


    @property
    def fire_enchanted(self):
        return 'fire_enchant' in self.buff.keys()


    def buff_calc(self, buff_type, is_multi=False):
        if is_multi:
            enhance = 1
            if buff_type in self.buff.keys():
                for item in self.buff[buff_type]:
                    enhance *= (item[0] + 1)

            return enhance
        else:
            add = 0
            if buff_type in self.buff.keys():
                for item in self.buff[buff_type]:
                    add += item[0]
            return add

    # 用于乘法运算的属性，使其数值正常
    def buff_calc_spec(self, buff_type):
        enhance = 1
        if buff_type in self.buff.keys():
            for item in self.buff[buff_type]:
                enhance *= max(1 - item[0], 0.00001)

        return enhance

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
        返回一个tuple，[0]为实际伤害量，[1]为攻击状态(-1: 闪避了, 0: 直接伤害, 1: 护盾被击破, 2: 护盾未击破), [2]为对生命本身而非护盾造成的伤害
        """
        shield_break = 0
        shield_damage = 0

        # 考虑闪避
        if random.random() < self.dodge and not magic:
            return 0, -1, 0

        # 护盾将会被优先攻击
        if self.shield > 0:
            # 预定护盾状态
            shield_break = 1
            # 即将造成这么多的伤害
            total_damage = damage
            # 暂存护盾值
            shield_damage = self.shield
            # 计算攻击护盾之后剩余的伤害
            damage = self._shield_hurt(damage)
            # 伤害全部被护盾挡下
            if damage == 0:
                return total_damage - damage, 2, 0

        if magic:
            real_damage = self._life_hurt(damage)
        else:
            real_damage = self._life_hurt(self._damage_reduce(damage))

        return real_damage + shield_damage, shield_break, real_damage

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
            raise NoTargetSelected('选择器没有选到任何的目标！效果信息：%s' % str(effect))

        param = effect['param']

        ret = []

        def do_phy_damage():
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
                'merge_key': {'target': self._self_replace(obj.name),'amount': real_damage},
                'param': {}
            })

        def do_magic_damage(damage):
            magic_damage = damage * self.spell_rate * fluctuation()
            real_damage, atk_status, _ = obj.take_damage(magic_damage, magic=True)
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

        # 普通攻击
        if effect['type'] == 'NORMAL_ATK':
            for obj in selector:
                atk_damage, is_crit = self.do_attack()
                real_damage, atk_status, hp_damage = obj.take_damage(atk_damage)
                # magic_enchant
                # 吸血
                self.recover(hp_damage * self.life_steal_rate)

                # miss
                if atk_status == -1:
                    ret.append({
                        'feedback': '{target}闪避了攻击',
                        'merge_key': {'target': self._self_replace(obj.name)},
                        'param': {}
                    })
                else:
                    if self.fire_enchanted:
                        do_magic_damage(self.attack * numerical['fire_enchant_rate'])
                        do_phy_damage()
                    else:
                        do_phy_damage()

        # 魔法伤害
        elif effect['type'] == 'MGC_DMG':
            for obj in selector:
                do_magic_damage(param[0][0])

        # 固定值攻击强化
        elif effect['type'] == 'PHY_ATK_BUFF_CONST':
            for obj in selector:
                real_added = obj.add_buff('attack_enhanced', param[0][0] * fluctuation(), param[1], buff_enhanced=True)
                ret.append({
                    'feedback': '强化了{target}{amount:.0f}点攻击，持续{duration}回合',
                    'merge_key': {'target': self._self_replace(obj.name), 'duration': param[1]},
                    'param': {'amount': real_added}
                })

        # 百分比强化
        elif effect['type'] == 'PHY_ATK_BUFF_RATE':
            for obj in selector:
                real_point = obj._attack_rate_to_pont(param[0][0])
                real_added = obj.add_buff('attack_enhanced', real_point * fluctuation(), param[1])
                ret.append({
                    'feedback': '强化了{target}{amount:.0f}点攻击，持续{duration}回合',
                    'merge_key': {'target': self._self_replace(obj.name), 'duration': param[1]},
                    'param': {'amount': real_added}
                })

        # 治疗
        elif effect['type'] == 'HEAL':
            for obj in selector:
                real_heal = obj.recover(param[0][0] * fluctuation())
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
                obj.add_buff('silence', True, param[1])
                ret.append({
                    'feedback': '沉默{target}{duration}回合',
                    'merge_key': {'duration': param[1]},
                    'param': {'target': self._self_replace(obj.name)}
                })

        # 净化
        elif effect['type'] == 'PURIFY':
            for obj in selector:
                obj.buff = {}
                ret.append({
                    'feedback': '清除了{target}所有的状态',
                    'merge_key': {},
                    'param': {'target': self._self_replace(obj.name)}
                })

        # 攻击削弱
        elif effect['type'] == 'ATK_DEBUFF':
            for obj in selector:
                real_minus = obj.add_buff('attack_weaken', param[0][0] * fluctuation(rate=0.95), param[1])
                ret.append({
                    'feedback': '削弱了{target}{minus_value:.0%}的攻击，持续{duration}回合',
                    'merge_key': {'target': self._self_replace(obj.name), 'duration': param[1]},
                    'param': {'minus_value': real_minus}
                })

        # 法术增强
        elif effect['type'] == 'MGC_BUFF_RATE':
            for obj in selector:
                real_added = obj.add_buff('spell_rate_enhanced', param[0][0] * fluctuation(rate=0.95), param[1])
                ret.append({
                    'feedback': '强化了{target}{amount:.0%}的法术强度，持续{duration}回合',
                    'merge_key': {'target': self._self_replace(obj.name), 'duration': param[1]},
                    'param': {'amount': real_added}
                })

        # 护甲衰减
        elif effect['type'] == 'DEF_DEC':
            for obj in selector:
                real_added = obj.add_buff('defence_weaken', param[0][0] * self.buff_rate * fluctuation(rate=0.8),
                                          param[1])
                ret.append({
                    'feedback': '削弱了{target}{amount:.1f}点防御，持续{duration}回合',
                    'merge_key': {'target': self._self_replace(obj.name), 'duration': param[1]},
                    'param': {'amount': real_added}
                })

        # 护甲提升
        elif effect['type'] == 'DEF_UP':
            for obj in selector:
                real_added = obj.add_buff('defence_enhanced', param[0][0] * fluctuation(rate=0.8), param[1],
                                          buff_enhanced=True)
                ret.append({
                    'feedback': '强化了{target}{amount:.1f}点防御，持续{duration}回合',
                    'merge_key': {'target': self._self_replace(obj.name), 'duration': param[1]},
                    'param': {'amount': real_added}
                })

        # 暴击伤害倍率提升
        elif effect['type'] == 'CRIT_RATE_BUFF':
            for obj in selector:
                real_added = obj.add_buff('crit_rate_enhanced', param[0][0] * fluctuation(), param[1],
                                          buff_enhanced=True)
                ret.append({
                    'feedback': '提升了{target}{amount:.0%}的暴击伤害倍率，持续{duration}回合',
                    'merge_key': {'target': self._self_replace(obj.name), 'duration': param[1]},
                    'param': {'amount': real_added}
                })

        # 暴击率提升
        elif effect['type'] == 'CRIT_CHANCE_BUFF':
            for obj in selector:
                real_added = obj.add_buff('crit_chance_enhanced', param[0][0] * fluctuation(0.9), param[1])
                ret.append({
                    'feedback': '提升了{target}{amount:.1%}的暴击率，持续{duration}回合',
                    'merge_key': {'target': self._self_replace(obj.name), 'duration': param[1]},
                    'param': {'amount': real_added}
                })

        # 闪避率提升
        elif effect['type'] == 'DODGE_BUFF':
            for obj in selector:
                real_added = obj.add_buff('dodge_enhanced', param[0][0] * fluctuation(0.9), param[1])
                ret.append({
                    'feedback': '提升了{target}{amount:.0%}的闪避率，持续{duration}回合',
                    'merge_key': {'target': self._self_replace(obj.name), 'duration': param[1]},
                    'param': {'amount': real_added}
                })

        # 恢复强度提升
        elif effect['type'] == 'RECOVER_BUFF_RATE':
            for obj in selector:
                real_added = obj.add_buff('recover_rate_enhanced', param[0][0] * fluctuation(), param[1])
                ret.append({
                    'feedback': '提升了{target}{amount:.1%}的恢复强度，持续{duration}回合',
                    'merge_key': {'target': self._self_replace(obj.name), 'duration': param[1]},
                    'param': {'amount': real_added}
                })

        # 恢复强度降低
        elif effect['type'] == 'RECOVER_DEC':
            for obj in selector:
                real_added = obj.add_buff('recover_rate_weaken', param[0][0] * fluctuation(), param[1])
                ret.append({
                    'feedback': '降低了{target}{amount:.1%}的恢复强度，持续{duration}回合',
                    'merge_key': {'target': self._self_replace(obj.name), 'duration': param[1]},
                    'param': {'amount': real_added}
                })

        # MP提高
        elif effect['type'] == 'MP_UP':
            for obj in selector:
                real_added, _ = obj.gain_mp(param[0][0] * fluctuation())
                ret.append({
                    'feedback': '增加了{target}{amount:.0f}点MP',
                    'merge_key': {'target': self._self_replace(obj.name)},
                    'param': {'amount': real_added}
                })

        # MP窃取 / MP减少
        elif effect['type'] == 'MP_STEAL':
            for obj in selector:
                stolen_mp = obj.mp_dec(param[0][0] * fluctuation())
                gain, _ = self.gain_mp(stolen_mp * param[1])
                if param[1] == 0:
                    ret.append({
                        'feedback': '减少了{target}{amount:.0f}点MP',
                        'merge_key': {'target': self._self_replace(obj.name)},
                        'param': {'amount': stolen_mp}
                    })
                else:
                    ret.append({
                        'feedback': '窃取了{target}{amount:.0f}点MP并回复了自己{gain:.0f}点MP',
                        'merge_key': {'target': self._self_replace(obj.name)},
                        'param': {'amount': stolen_mp, 'gain': gain}
                    })

        # 生命窃取倍率提升
        elif effect['type'] == 'LIFE_STEAL_UP':
            for obj in selector:
                real_added = obj.add_buff('life_steal_enhanced', param[0][0] * fluctuation(), param[1])
                ret.append({
                    'feedback': '提升了{target}{amount:.0%}的生命窃取倍率，持续{duration}回合',
                    'merge_key': {'target': self._self_replace(obj.name), 'duration': param[1]},
                    'param': {'amount': real_added}
                })

        # 法术倍率降低
        elif effect['type'] == 'SPELL_DEC':
            for obj in selector:
                real_added = obj.add_buff('spell_rate_weaken', param[0][0] * fluctuation(0.95), param[1])
                ret.append({
                    'feedback': '降低了{target}{amount:.1%}的法术倍率，持续{duration}回合',
                    'merge_key': {'target': self._self_replace(obj.name), 'duration': param[1]},
                    'param': {'amount': real_added}
                })

        # 火焰附魔 (反正是一回事儿)
        elif effect['type'] == 'FIRE_ENCHANT':
            for obj in selector:
                real_added = obj.add_buff('fire_enchant', True, param[1])
                ret.append({
                    'feedback': '为{target}添加了火焰附魔，持续{duration}回合',
                    'merge_key': {'target': self._self_replace(obj.name), 'duration': param[1]},
                    'param': {}
                })

        else:
            raise ValueError('出现了未知的效果类型' + effect['type'])
        return ret

    # ————————————————————————————
    #           效果处理
    # ————————————————————————————

    def add_buff(self, buff_type: str, value, time, buff_enhanced=False):
        """
        使用这个函数添加buff。
        :param buff_type: buff的种类，buff有后缀，enhanced为增益效果，weaken为减益效果，这是重要的消除buff的依据。
        :param value: buff值
        :param time: 持续回合数
        :param buff_enhanced: 这个buff是否会被buff生效者的buff_rate所影响。
        """

        if buff_enhanced:
            value *= self.buff_rate

        if buff_type not in self.buff:
            self.buff[buff_type] = []

        self.buff[buff_type].append((value, time))
        return value

    def recover(self, recovery):
        """
        生命恢复。传入恢复量
        超过最大值的将会被舍弃
        返回实际恢复量
        """
        to_recover = recovery * self.recover_rate
        pre_hp = self.HP
        self.HP += to_recover
        if self.HP <= self.attributes['HP']:
            return to_recover
        else:
            diff = self.attributes['HP'] - pre_hp
            self.HP = self.attributes['HP']
            return diff

    def give_shield(self, value):
        """
        添加护盾时使用，传入护盾量
        护盾不会叠加，只会取最大值
        返回实际护盾添加量
        """
        value *= self.buff_rate
        if self.shield >= value:
            return 0
        else:
            diff = value - self.shield
            self.shield = value
            return diff

    def mp_dec(self, value):
        cur_mp = self.MP
        self.MP -= value
        if self.MP < 0:
            self.MP = 0
            return cur_mp
        else:
            return value

    def gain_mp(self, value):
        """
        MP增加的时候使用，函数会保证MP值不超过1000点
        返回(实际增加量, 溢出量)的tuple
        """
        cur_mp = self.MP
        self.MP += value
        if self.MP > 1000:
            overflow = self.MP - 1000
            self.MP = 1000
            return 1000 - cur_mp, overflow
        else:
            return value, 0

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
        self.gain_mp(damage_percent * 1000 * numerical['life_to_mp'])
        return damage

    def _damage_reduce(self, damage):
        """
        计算护甲伤害减免，传入伤害量。
        返回护甲减免后的伤害值
        """
        damage_decrease = 1 + numerical['def_rate'] * self.defence
        if damage_decrease < 0.4:
            damage_decrease = 0.4
        return damage / damage_decrease

    def _attack_rate_to_pont(self, rate):
        """
        如果一个技能涉及到百分比强化攻击力，调用这个函数，传入提升量。
        返回实际战斗力提升点数
        """
        return self.attributes['attack'] * rate

    def _self_replace(self, chara_name: str) -> str:
        if chara_name == self.name:
            return '自身'
        return f'[{chara_name}]'

    def __repr__(self):
        S = self.name + ', '
        S += '%.0f/%.0f, ' % (self.HP, self.attributes['HP'])
        S += 'shield: %.0f, ' % self.shield
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


def fluctuation(rate=None):
    if rate:
        return biased(1, rate)[0]
    else:
        return biased(1, numerical['damage_fluctuation'])[0]


if __name__ == '__main__':
    pass
