from __future__ import annotations

from typing import TypedDict

from typing_extensions import NotRequired


class Alternative(TypedDict):
    transcript: str
    confidence: float


class Result(TypedDict):
    alternative: list[Alternative]
    final: bool


class GoogleResponse(TypedDict):
    result: list[Result]
    result_index: NotRequired[int]
