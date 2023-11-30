from __future__ import annotations

from typing import TypedDict


class Alternative(TypedDict):
    transcript: str
    confidence: float


class Result(TypedDict):
    alternative: list[Alternative]


class GoogleResponse(TypedDict):
    result: list[Result]
