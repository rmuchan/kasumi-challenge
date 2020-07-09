from typing import Dict, Any, Iterable

from rand import randomize


def create_skill(template: Dict[str, Any], is_unique: bool) -> Dict[str, Any]:
    skill = randomize(template)
    for effect in skill['effect']:
        if 'param' not in effect:
            effect['param'] = effect['unique_param' if is_unique else 'skill_param']
            del effect['skill_param']
            del effect['unique_param']
    return skill


def get_skill_desc(skill: Dict[str, Any]) -> str:
    """生成技能描述。

    以技能desc字段为模板，传入技能效果参数。模板中可以插入形如{a[b]}的字符串，将被替换为第a个效果的第b个参数（均从0开始计数）。
    参数如果由biased随机函数生成，则会以8.00(SS)的形式同时插入其数值和评级，否则只插入其数值（保留两位小数）。

    :param skill: 技能
    :return: 插入具体数值的技能描述
    """
    return skill['desc'].format(*([_get_param_desc(y) for y in x['param']] for x in skill['effect']))


def _get_param_desc(param) -> str:
    if isinstance(param, Iterable):
        return '{0:.2f}({1})'.format(*param)
    else:
        return '{:.2f}'.format(param)
