from abc import ABC, abstractmethod
from typing import Optional, Any


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
            await self.do_send(send_msg)

    async def input(self, prompt: str) -> str:
        await self.do_send(prompt)
        return await self.do_input()

    @abstractmethod
    async def do_send(self, msg: str) -> None:
        pass

    @abstractmethod
    async def do_input(self) -> str:
        pass

    @abstractmethod
    def store(self, key: str, value: Any) -> None:
        pass

    @abstractmethod
    def retrieve(self, key: str) -> Optional[Any]:
        pass
