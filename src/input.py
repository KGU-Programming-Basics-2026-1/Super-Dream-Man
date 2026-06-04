# input.py

from collections import deque
from dataclasses import dataclass
from time import time
from typing import Callable, Deque, Optional, Union


@dataclass
class InputEvent:
    type: str
    code: Optional[Union[str, int]] = None
    x: Optional[int] = None
    y: Optional[int] = None
    button: Optional[str] = None
    pressed: Optional[bool] = None
    wheel: Optional[int] = None
    timestamp: float = 0.0

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time()


class InputQueue:
    def __init__(self, capacity: int = 256):
        self._queue: Deque[InputEvent] = deque(maxlen=capacity)

    def push(self, event: InputEvent) -> None:
        self._queue.append(event)

    def pop(self) -> Optional[InputEvent]:
        return self._queue.popleft() if self._queue else None

    def clear(self) -> None:
        self._queue.clear()

    def has_pending(self) -> bool:
        return bool(self._queue)

    def __len__(self) -> int:
        return len(self._queue)


class InputHandler:
    def __init__(self, queue_capacity: int = 256):
        self.queue = InputQueue(queue_capacity)

    def keyboard_interrupt(self, key_code: Union[str, int], pressed: bool = True) -> None:
        event = InputEvent(type="keyboard", code=key_code, pressed=pressed)
        self.queue.push(event)

    def mouse_interrupt(
        self,
        x: int,
        y: int,
        button: Optional[str] = None,
        pressed: Optional[bool] = None,
        wheel: int = 0,
    ) -> None:
        event = InputEvent(
            type="mouse",
            x=x,
            y=y,
            button=button,
            pressed=pressed,
            wheel=wheel,
        )
        self.queue.push(event)

    def poll(self) -> Optional[InputEvent]:
        return self.queue.pop()

    def process(self, callback: Callable[[InputEvent], None]) -> None:
        while self.queue.has_pending():
            event = self.queue.pop()
            if event is not None:
                callback(event)

    def continuous_process(self, callback: Callable[[InputEvent], None], max_events: int = 64) -> None:
        count = 0
        while self.queue.has_pending() and count < max_events:
            event = self.queue.pop()
            if event is not None:
                callback(event)
                count += 1


def default_input_callback(event: InputEvent) -> None:
    if event.type == "keyboard":
        state = "pressed" if event.pressed else "released"
        print(f"Keyboard {state}: {event.code}")
    elif event.type == "mouse":
        mouse_info = f"Mouse at ({event.x}, {event.y})"
        if event.button is not None:
            state = "pressed" if event.pressed else "released"
            mouse_info += f", button {event.button} {state}"
        if event.wheel:
            mouse_info += f", wheel {event.wheel}"
        print(mouse_info)
