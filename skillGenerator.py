import json

magic_high = {"type": "MGC_DMG", "target": {"type": "RAND", "team": 0, "limit": 1}, "skill_param": [{"random": "biased", "expect": 80, "min": 64},], "unique_param": [{"random": "biased", "expect": 160, "min": 120}]}
magic_low = {"type": "MGC_DMG", "target": {"type": "RAND", "team": 0, "limit": 1}, "skill_param": [{"random": "biased", "expect": 40, "min": 32},], "unique_param": [{"random": "biased", "expect": 80, "min": 60}]}

const_buff_self_low = {
            "type": "PHY_ATK_BUFF_CONST",
            "target": {
                "type": "SELF",
                "team": 1,
                "limit": 1
            },
            "skill_param": [
                {
                    "random": "biased",
                    "expect": 20,
                    "min": 16
                },
                2
            ],
            "unique_param": [
                {
                    "random": "biased",
                    "expect": 45,
                    "min": 38
                },
                2
            ]
        }

rate_buff_self_low = {
            "type": "PHY_ATK_BUFF_RATE",
            "target": {
                "type": "SELF",
                "team": 1,
                "limit": 1
            },
            "skill_param": [
                {
                    "random": "biased",
                    "expect": 0.1,
                    "min": 0.08
                },
                2
            ],
            "unique_param": [
                {
                    "random": "biased",
                    "expect": 0.21,
                    "min": 0.18
                },
                2
            ]
        }



rate_buff_team_low = {
            "type": "PHY_ATK_BUFF_CONST",
            "target": {
                "type": "ALL",
                "team": 1,
                "limit": 1
            },
            "skill_param": [
                {
                    "random": "biased",
                    "expect": 0.026,
                    "min": 0.02
                },
                2
            ],
            "unique_param": [
                {
                    "random": "biased",
                    "expect": 0.58,
                    "min": 0.53
                },
                2
            ]
        }

const_buff_team_low = {
            "type": "PHY_ATK_BUFF_RATE",
            "target": {
                "type": "ALL",
                "team": 1,
                "limit": 1
            },
            "skill_param": [
                {
                    "random": "biased",
                    "expect": 5,
                    "min": 4
                },
                2
            ],
            "unique_param": [
                {
                    "random": "biased",
                    "expect": 12,
                    "min": 10
                },
                2
            ]
        }


buff_low = [const_buff_self_low, const_buff_team_low, rate_buff_self_low, rate_buff_team_low]

J = {
    "name": {
        "random": "choice",
        "values": [
            "魔法震荡",
            "心灵震击",
        ]
    },
    "desc": "对敌人造成{0[0]}点魔法伤害，然后提升自身{1[0]}物理攻击力",
    "feedback": "这里是反馈",
    "feedback-loop": "这里的反馈内容会循环",
    "effect": []
}



with open('skill2.json', 'w+') as F:
    json.dump(J, F, indent=4, ensure_ascii=False)