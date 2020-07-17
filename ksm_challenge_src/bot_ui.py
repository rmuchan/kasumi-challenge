import asyncio
from typing import Optional, Any, Dict

from nonebot import NoneBot, context_id
from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot.typing import Context_T

from .data import data
from .interact import UI

# context id -> running UI
_running: Dict[str, 'BotContextUI'] = {}


class BotContextUI(UI):
    def __init__(self, bot: NoneBot, ctx: Context_T):
        super().__init__()
        self._bot = bot
        self._ctx = ctx
        self._ctx_id = context_id(ctx)
        self._pending_input = None
        self._store = data.saves[self.uid()] or {}

    def uid(self) -> int:
        return self._ctx['user_id']

    async def do_send(self, msg: str) -> None:
        await self._bot.send(self._ctx, msg)

    async def do_input(self) -> str:
        """
        获取用户输入。最大等待时长由bot配置的SESSION_EXPIRE_TIMEOUT项指定。
        该函数只能在正在通过run执行函数的UI上调用。

        :return: 来自self._ctx上下文的下一条消息
        :raise ValueError: 若UI未在通过run执行函数
        :raise BotContextUI._CancelException: 若超出最大等待时长仍未收到消息
        """
        if _running.get(self._ctx_id) is not self:
            raise ValueError
        loop = asyncio.get_event_loop()
        self._pending_input = loop.create_future()
        try:
            return await asyncio.wait_for(self._pending_input, self._bot.config.SESSION_EXPIRE_TIMEOUT.total_seconds())
        except asyncio.TimeoutError:
            raise BotContextUI._CancelException

    def store(self, key: str, value: Any) -> None:
        self._store[key] = value
        data.saves[self.uid()] = self._store

    def retrieve(self, key: str) -> Optional[Any]:
        return self._store.get(key)

    def run(self, func, *args, **kwargs):
        """
        使用本UI执行函数。上下文ID相同的UI同一时刻只能有一个通过run执行函数。
        func会以await func(self, *args, **kwargs)的形式调用。
        该函数即刻返回，不等待func执行结束。

        :param func: 待执行的函数。必须为异步函数，且接受至少一个位置参数。
        :param args: 需传入的其他位置参数
        :param kwargs: 需传入的其他命名参数
        :return: 无
        :raise BotContextUI.RunningException: 若有上下文ID相同的UI正在通过run执行函数
        """
        async def _run():
            try:
                await func(self, *args, **kwargs)
            except BotContextUI._CancelException:
                pass
            finally:
                del _running[self._ctx_id]

        if self._ctx_id in _running:
            raise BotContextUI.RunningException
        _running[self._ctx_id] = self
        asyncio.ensure_future(_run())

    @property
    def input_pending(self) -> bool:
        """
        指示UI是否正在等待输入。
        """
        return self._pending_input is not None

    @input_pending.setter
    def input_pending(self, msg: str):
        """
        为UI提供输入。若UI当前未在等待输入则没有效果。
        """
        if self._pending_input is not None:
            self._pending_input.set_result(msg)
            self._pending_input = None

    class _CancelException(Exception):
        pass

    class RunningException(Exception):
        pass


@on_command(('_ui', 'feed_input'))
async def _(session: CommandSession):
    ctx_id = context_id(session.ctx)
    ui = _running.get(ctx_id)
    if ui is not None:
        ui.input_pending = session.current_arg


@on_natural_language(only_to_me=False)
async def _(session: NLPSession):
    msg = session.msg_text
    ctx_id = context_id(session.ctx)
    ui = _running.get(ctx_id)
    if msg and ui is not None and ui.input_pending:
        return IntentCommand(80, ('_ui', 'feed_input'), current_arg=msg)
