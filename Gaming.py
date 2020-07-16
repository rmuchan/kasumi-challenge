from abc import ABC, abstractmethod
from typing import List
from GameChar import GameChar


class Gaming(ABC):
    def __init__(self, team_a: List[GameChar], team_b: List[GameChar]):
        self.team_a = team_a
        self.team_b = team_b
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

            # 技能发动、攻击、效果执行
            # 然后buff结算、减冷却
            self._skill_check('a')
            self._status_manage('a')

            self._skill_check('b')
            self._status_manage('b')

            self.team_a = self._death_check('a')
            self.team_b = self._death_check('b')
            

    # TODO 选择器
    def selector(self, target, camp: str, initiator: GameChar):

        return [initiator]

    def _death_check(self, team_name):
        if team_name == 'a':
            team = self.team_a
        elif team_name == 'b':
            team = self.team_b
        else:
            raise ValueError("team_name只能在'a'和'b'中选择")

        now_team = []
        for chara in team:
            if chara.not_dead:
                now_team.append(chara)
            else:
                pass
                # TODO 汇报死亡消息

        return now_team

    def _skill_check(self, team_name):

        if team_name == 'a':
            team = self.team_a
        elif team_name == 'b':
            team = self.team_b
        else:
            raise ValueError("team_name只能在'a'和'b'中选择")

        for chara in team:
            skill_gotten = chara.skill_activate()
            if skill_gotten is not None:
                for effect in skill_gotten['effect']:
                    selected = self.selector(effect['target'], team_name, chara)
                    feedback = chara.use_effect(selected, effect['param'])
                    # TODO print(feedback)
            else:
                pass
                # 说明MP不够用
                # print('TP不足')

    def _status_manage(self, team_name):

        if team_name == 'a':
            team = self.team_a
        elif team_name == 'b':
            team = self.team_b
        else:
            raise ValueError("team_name只能在'a'和'b'中选择")

        for chara in team:
            chara.buff_fade()
            chara.skill_cooldown()
            chara.turn_mp_gain()


    @abstractmethod
    def _msg_append(self, msg_text):
        pass

    @abstractmethod
    def _msg_send(self):
        pass
