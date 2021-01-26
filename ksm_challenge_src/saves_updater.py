def update(d: dict):
    """
    更新存档，根据存档的"$version"字段依次调用各个更新函数。
    :param d: 已加载的存档文件
    :return: None. 原地修改d
    """
    version = d.get('$version', 0)
    for _, updater in _updaters[_get_start(version):]:
        updater(d)
    d['$version'] = current_version


def _get_start(version: int) -> int:
    if not _start_map:
        _start_map[:] = [0] * (current_version + 1)
        last_ver = 0
        for idx, (ver, _) in enumerate(_updaters):
            if last_ver != ver:
                _start_map[last_ver] = idx
                last_ver = ver
        _start_map[last_ver] = len(_updaters)
    return _start_map[version]


def _remove_proto_character(d: dict):
    d.pop('proto_character', None)


# 版本号从1开始连续编排，每个版本可以有多个更新函数，会依次调用
_updaters = [
    (1, _remove_proto_character)
]
_start_map = []
current_version = _updaters[-1][0] if _updaters else 0
