import random
from abc import ABC, abstractmethod
from typing import List
from GameChar import GameChar


class Gaming(ABC):
    def __init__(self, team_a: List[dict], team_b: List[dict]):
        self.team_a = [GameChar(x) for x in team_a]
        self.team_b = [GameChar(x) for x in team_b]
        self.turn = 1

    def start(self):
        while True:
            # 获胜状态判断
            if len(self.team_a) == 0 and len(self.team_b) == 0:
                return 'all_dead'
            if len(self.team_a) == 0:
                return 'b_win'
            if len(self.team_b) == 0:
                return 'a_win'

            print('回合数：', self.turn)

            # 技能发动、攻击、效果执行
            # 然后buff结算、减冷却
            self._skill_check('a')
            self._status_manage('a')

            self._skill_check('b')
            self._status_manage('b')

            self.team_a = self._death_check('a')
            self.team_b = self._death_check('b')

            self.turn += 1

    def selector(self, target, team_name: str, initiator: GameChar):
        type_ = target['type']
        if type_ == 'SELF':
            return [initiator]
        if type_ == 'OTHER':
            return list(filter(lambda x: x is not initiator, self._get_team(team_name)))

        if target['team'] == 0:
            team_name = {'a': 'b', 'b': 'a'}[team_name]
        team = self._get_team(team_name)

        if type_ == 'ALL':
            return team
        if type_ == 'RAND':
            result = team * (target['limit'] // len(team)) + random.sample(team, target['limit'] % len(team))
            random.shuffle(result)
            return result

        key, reverse = {
            'LIFEMOST': (lambda x: x.hp_percentage, True),
            'LIFELEAST': (lambda x: x.hp_percentage, False),
            'ATKMOST': (lambda x: x.attack, True),
            'ATKLEAST': (lambda x: x.attack, False)
        }[type_]
        return sorted(team, key=key, reverse=reverse)[:target['limit']]

    def _death_check(self, team_name):
        team = self._get_team(team_name)

        now_team = []
        for chara in team:
            if chara.not_dead:
                now_team.append(chara)
            else:
                pass
                # TODO 汇报死亡消息

        return now_team

    def _skill_check(self, team_name):
        team = self._get_team(team_name)

        for chara in team:
            skill_gotten = chara.skill_activate()
            if skill_gotten is not None:
                print(chara.name, skill_gotten['name'], chara.MP)
                for effect in skill_gotten['effect']:
                    selected = self.selector(effect['target'], team_name, chara)
                    feedback = chara.use_effect(selected, effect)
                    for i in feedback['params']:
                        print(feedback['feedback'].format(**i))
                    # TODO 更好的UI的展示内容
            else:
                pass
                # 说明MP不够用
                # print('TP不足')

    def _status_manage(self, team_name):
        team = self._get_team(team_name)

        for chara in team:
            chara.buff_fade()
            chara.skill_cooldown()
            chara.turn_mp_gain()

    def _get_team(self, team_name):
        return getattr(self, f'team_{team_name}')

    # @abstractmethod
    def _msg_append(self, msg_text):
        pass

    # @abstractmethod
    def _msg_send(self):
        pass
