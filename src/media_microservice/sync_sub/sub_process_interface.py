"""Syncronized 'Fail-fast' Subprocess builder"""
from __future__ import annotations

import logging
from abc import ABCMeta
from abc import abstractmethod
from typing import Any
from typing import Type

LambdaEvent = dict[str, Any]


class SubProcess(metaclass=ABCMeta):
    """Abstract Fail-Fast SubProcess

    Args:
        event(LambdaEvent): Lambda Event.
        deps(dict[str, Any]): Result of former SubProcess(s).
    """

    deps: dict[str, Any]
    event: LambdaEvent

    def __init__(self, event: LambdaEvent, deps: dict[str, Any]) -> None:
        self.deps = deps
        self.event = event

    @abstractmethod
    def execute(self) -> None:
        """Execute Subprocess"""
        raise NotImplementedError

    @abstractmethod
    def rollback(self) -> None:
        """Rollback Subprocess"""
        raise NotImplementedError


class Sync:
    """Concrete Subprocess Builder

    Raises:
        e: Arbitrary exception thrown by SubProcess execution.
    """

    services: list[Type[SubProcess]]
    # Result of Synchronized Process(s)
    result: dict[str, Any]

    def __init__(self, initial: dict[str, Any] | None = None) -> None:
        if not initial:
            _initial = {}
        else:
            _initial = initial
        self.result = _initial
        self.services = []

    def add(self, service: Type[SubProcess]) -> Sync:
        """Add Subprocess

        Args:
            service (Type[SubProcess[R]]): SubProcess Child Class.

        Returns:
            sync(Sync): self
        """
        self.services.append(service)

        return self

    def rollback_all(self, executed: list[SubProcess]) -> None:
        """Rollback all SubProcess Executions."""
        for s in executed:
            s.rollback()

    def execute(self, event: LambdaEvent) -> dict[str, Any]:
        """Execute SubProcess(s)

        Args:
            event (LambdaEvent): Lambda Event.

        Returns:
            result(dict[str, Any]): Result of subprocess(s).

        Raises:
            Exception: Error while executing SubProcess(s).
        """
        executed = []
        for s in self.services:
            try:
                service: SubProcess = s(event, self.result)

                executed.append(service)
                service.execute()
            except Exception as e:
                logging.error("Sync Subprocess %s failed.\nReason: %s", s.__name__, e)
                self.rollback_all(executed)
                raise e

        return self.result
