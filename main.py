import asyncio
import json
from typing import Optional, Any
import matplotlib.pyplot as plt

from ksm_challenge_src.Gaming import Gaming
from ksm_challenge_src.attr_calc import game_char_gen
from ksm_challenge_src.character import create_character, print_character
from ksm_challenge_src.interact import UI
from ksm_challenge_src.talent_calc import show_talent, upgrade_talent


class CLI(UI):
    def __init__(self, uid: int):
        super().__init__()
        self._uid = uid
        self._is_first = True
        self._store = {}
        # try:
        #     with open(f'store_{self._uid}.json', 'r') as f:
        #         self._store = json.load(f)
        # except:
        #     self._store = {}

    def uid(self) -> int:
        return self._uid

    async def do_send(self, msg: str):
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


async def main():
    chars = []
    for i in range(8):
        ui = CLI(i)
        c = await create_character(ui)
        chars.append(c)
        await print_character(ui, c)
    gcs = [game_char_gen(x) for x in chars]
    game = Gaming(gcs[:4], gcs[4:], CLI(0))
    print(await game.start())


async def main2():
    tot = [0 for _ in range(41)]
    tmo = 0
    for ix in range(1000):
        print(ix)
        chars = []
        for i in range(8):
            ui = CLI(i)
            c = await create_character(ui)
            chars.append(c)
            await print_character(ui, c)
        gcs = [game_char_gen(x) for x in chars]
        game = Gaming(gcs[:4], gcs[4:], CLI(0))
        result, turn = await game.start()
        tot[turn] += 1
        if result == 'timeout':
            tmo += 1
    print(tmo)
    plt.plot(list(range(41)), tot)
    plt.show()


if __name__ == '__main__':
    asyncio.run(main())
