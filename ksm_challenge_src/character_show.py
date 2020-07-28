from ksm_challenge_src.attr_calc import game_char_gen
from ksm_challenge_src.skill import get_skill_desc

a = {
  "proto_character": None,
  "character": {
    "name": "小六",
    "race": "Huntars",
    "race_id": 5,
    "exp": 1,
    "str_build": [
      1.0802648890238769,
      "S"
    ],
    "int_build": [
      1.046781713630093,
      "S"
    ],
    "per_build": [
      0.8876723754511122,
      "B"
    ],
    "life_build": [
      0.7674253281174112,
      "C"
    ],
    "def_base": [
      1.278935141142377,
      "S"
    ],
    "defense_str_rate": 0.2294608284732037,
    "magic_int_rate": 0.19148488524356433,
    "health_per_rate": 0.23061668932407808,
    "attack_rate": [
      3.1922215711599278,
      "A"
    ],
    "passive": {
      "desc": "闪避+10%",
      "buff": {
        "dodge": 0.1
      }
    },
    "skill_1": {
      "chance": 0.2797351323443701,
      "cooldown": 0,
      "mp_cost": 69,
      "name": "冰锥术",
      "effect": [
        {
          "name": "冰锥术",
          "desc": "随机对{target[limit]}个敌人造成{param[0]}点魔法伤害",
          "weight": 3,
          "type": "MGC_DMG",
          "target": {
            "type": "RAND",
            "team": 0,
            "limit": 1
          },
          "param": [
            [
              323.3481740343789,
              "SS"
            ]
          ]
        }
      ]
    },
    "skill_2": {
      "chance": 0.08860239565839906,
      "cooldown": 2,
      "mp_cost": 68,
      "name": "水球术",
      "effect": [
        {
          "name": "水球术",
          "desc": "随机对{target[limit]}个敌人造成{param[0]}点魔法伤害",
          "weight": 3,
          "type": "MGC_DMG",
          "target": {
            "type": "RAND",
            "team": 0,
            "limit": 1
          },
          "param": [
            [
              304.27275063026264,
              "S"
            ]
          ]
        }
      ]
    },
    "skill_3": {
      "chance": 0.060848470482242546,
      "cooldown": 2,
      "mp_cost": 84,
      "name": "冰锥术",
      "effect": [
        {
          "name": "冰锥术",
          "desc": "随机对{target[limit]}个敌人造成{param[0]}点魔法伤害",
          "weight": 3,
          "type": "MGC_DMG",
          "target": {
            "type": "RAND",
            "team": 0,
            "limit": 2
          },
          "param": [
            [
              159.0026328946671,
              "S"
            ]
          ]
        }
      ]
    },
    "unique": {
      "chance": 0.08122165808882793,
      "cooldown": 2,
      "mp_cost": 66,
      "name": "攻击激励",
      "effect": [
        {
          "name": "攻击激励",
          "desc": "强化自身{param[0]}点攻击，持续{param[1]}回合",
          "weight": 1,
          "type": "PHY_ATK_BUFF_CONST",
          "target": {
            "type": "SELF",
            "team": 1,
            "limit": 1
          },
          "param": [
            [
              51.867650986887554,
              "SS"
            ],
            3
          ]
        }
      ]
    }
  }
}

def show_chara_info(save: dict):
    S = '------玩家信息------\n'
    if save['proto_character'] is not None:
        return False

    char = game_char_gen(save['character'])

    S += '名字：%s | 种族：%s\n' % (char['name'], save['character']['race'])
    S += '力量：%.0f | 敏捷：%.0f\n' % (char['str'], char['int'])
    S += '感知：%.0f | 生命：%.0f\n' % (char['per'], char['HP'])
    S += '攻击：%.0f | 防御：%.1f\n' % (char['attack'], char['defence'])
    S += '恢复强度：{:.0%}\n'.format(char['recover_rate'])
    S += '法术倍率：{:.0%}\n'.format(char['spell_rate'])
    S += '增益幅度：{:.0%}\n'.format(char['buff_rate'])
    S += '暴击倍率：{:.0%}\n'.format(char['crit_rate'])
    S += '生命窃取：{:.0%}\n'.format(char['life_steal_rate'])
    S += '闪避率：{:.1%}\n'.format(char['dodge'])
    S += '------技能组------\n'
    S += '主技能：\n' + get_skill_desc(char['skill_1'], is_unique=False) + '\n'
    S += '副技能：\n' + get_skill_desc(char['skill_2'], is_unique=False) + '\n'
    S += '小技能：\n' + get_skill_desc(char['skill_3'], is_unique=False) + '\n'
    S += '必杀技：\n' + get_skill_desc(char['unique'], is_unique=True) + '\n'

    print(char)
    return S


if __name__ == '__main__':
    print(show_chara_info(a))



