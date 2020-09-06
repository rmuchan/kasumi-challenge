import asyncio
import json
from typing import Optional, Any
import matplotlib.pyplot as plt

from ksm_challenge_src.Gaming import Gaming
from ksm_challenge_src.attr_calc import game_char_gen
from ksm_challenge_src.boss_gen import boss_gen
from ksm_challenge_src.character import create_character, print_character
from ksm_challenge_src.interact import UI
from ksm_challenge_src.talent_calc import show_talent, upgrade_talent
from ksm_challenge_src.version import log_file



class CLI(UI):
    def __init__(self, uid: int, debug_mode=False):
        super().__init__()
        self._uid = uid
        self._is_first = True
        self._store = {}
        self.debug_mode = debug_mode
        # try:
        #     with open(f'store_{self._uid}.json', 'r') as f:
        #         self._store = json.load(f)
        # except:
        #     self._store = {}

    def uid(self) -> int:
        return self._uid

    async def do_send(self, msg: str):
        if not self.debug_mode:
            print(msg)
            print()

    async def do_input(self) -> str:
        if self._is_first:
            self._is_first = False
            return f'甲乙丙丁戊己庚辛'[self._uid]
        return '1'
        # return input()

    def store(self, key: str, value: Any) -> None:
        if value is None:
            del self._store[key]
        else:
            self._store[key] = value
        # with open(f'store_{self._uid}.json', 'w') as f:
        #     json.dump(self._store, f, indent=2, ensure_ascii=False)

    def retrieve(self, key: str) -> Optional[Any]:
        return self._store.get(key)

    def abort(self) -> None:
        exit(1)


with open('ksm_challenge_src/data/boss-pool/pedestrian.json') as FILE:
    boss = json.load(FILE)

test_level = 30

async def main():
    chars = []
    for i in range(8):
        ui = CLI(i)
        c = await create_character(ui)
        chars.append(c)
        await print_character(ui, c)
    gcs = [game_char_gen(x, test_lv=test_level) for x in chars]
    game = Gaming(gcs[:4], boss_gen(boss, test_level)['bosses'], CLI(0))
    print(await game.start(testing_mode=True))


async def main2():
    time_limit = 31
    test_amount = 200
    lvl_list = [1, 15, 30]
    turn_count = {i:[0 for _ in range(time_limit + 1)] for i in lvl_list}
    time_out = {i: 0 for i in lvl_list}
    a_win = {i: 0 for i in lvl_list}
    for lvl in lvl_list:
        for ix in range(test_amount):
            if ix % 50 == 0:
                print(lvl, ix)
            chars = []
            for i in range(4):
                ui = CLI(i, debug_mode=True)
                c = await create_character(ui)
                chars.append(c)
                await print_character(ui, c)
            gcs = [game_char_gen(x, test_lv=lvl) for x in chars]
            game = Gaming(gcs[:4], boss_gen(boss, lvl)['bosses'], CLI(0,debug_mode=True))
            result, turn = await game.start(testing_mode=True)
            turn_count[lvl][turn] += 1
            if result == 'timeout':
                time_out[lvl] += 1
            if result == 'a_win':
                a_win[lvl] += 1
        turn_count[lvl][29] = time_out[lvl]

    for lvl in lvl_list:
        print('--------')
        print(lvl, (a_win[lvl] / test_amount) * 100, '%')
        plt.plot(list(range(time_limit + 1)), turn_count[lvl],label=str(lvl) + ('[%.0f%%]' % (a_win[lvl] / test_amount * 100)))
    plt.legend()
    plt.show()

def gen_log():
    with open('doc/更新日志.md', 'w') as F:
        for item in log_file:
            F.write(f'### {item["version"]}\n')
            extra = item["log"].replace('\n', '  \n')
            F.write(f'  {extra}\n\n')


# TODO 减攻击调查一下
#TODO 物理减自己血两次攻击
#TODO 破盾一击

if __name__ == '__main__':
    #asyncio.run(main())
    gen_log()

