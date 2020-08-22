from abc import ABC, abstractmethod
from typing import Optional, Any, Callable

output = {}

class UI(ABC):
    def __init__(self):
        self._pending_msg = ''

    @abstractmethod
    def uid(self) -> int:
        pass

    def append(self, msg: str) -> None:
        self._pending_msg += msg
        self._pending_msg += '\n'

    async def send(self, msg: Optional[str] = None) -> None:
        if msg is not None:
            self.append(msg)
        send_msg = self._pending_msg.rstrip()
        self._pending_msg = ''
        if send_msg:
            output[self.uid()] = send_msg
            await self.do_send(send_msg)

    async def input(self, prompt: Optional[str] = None, *,
                    is_valid: Callable[[str], bool] = lambda _: True, attempts: int = 12) -> str:
        if prompt:
            await self.do_send(prompt)
        for _ in range(attempts):
            inp = await self.do_input()
            if is_valid(inp):
                return inp
        self.abort()

    @abstractmethod
    async def do_send(self, msg: str) -> None:
        pass

    @abstractmethod
    async def do_input(self) -> str:
        pass

    @abstractmethod
    def abort(self) -> None:
        pass

    @abstractmethod
    def store(self, key: str, value: Any) -> None:
        pass

    @abstractmethod
    def retrieve(self, key: str) -> Optional[Any]:
        pass
