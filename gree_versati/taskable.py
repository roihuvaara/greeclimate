from __future__ import annotations

import asyncio
import logging
from asyncio import Task
from asyncio.events import AbstractEventLoop
from typing import List, Optional

_LOGGER = logging.getLogger(__name__)


class Taskable:
    """Mixin class for objects that can be run as tasks."""

    def __init__(self, loop: Optional[AbstractEventLoop] = None):
        self._loop: AbstractEventLoop = loop or asyncio.get_event_loop()
        self._tasks: List[Task] = []

    @property
    def tasks(self) -> List[Task]:
        """Returns the outstanding tasks waiting completion."""
        return self._tasks

    def _task_done_callback(self, task):
        if task.exception():
            _LOGGER.exception("Uncaught exception", exc_info=task.exception())
        self._tasks.remove(task)

    def _create_task(self, coro) -> Task:
        """Create and track tasks that are being created for events."""
        task = self._loop.create_task(coro)
        self._tasks.append(task)
        task.add_done_callback(self._task_done_callback)
        return task
