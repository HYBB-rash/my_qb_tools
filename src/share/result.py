from dataclasses import dataclass
from typing import Generic, TypeVar, Union

T = TypeVar("T")
E = TypeVar("E")

"""
同一层中混用 `Result` 与“抛异常”：

之所以一边是异常，一边是Result，是因为如果这个错误需要上层去判断怎么处理，我就会使用Result风格来处理。

但如果业务函数确认这里不应该出现异常，我就会 raise 直接中断。
"""


@dataclass(slots=True)
class Ok(Generic[T]):
    value: T


@dataclass(slots=True)
class Err(Generic[E]):
    error: E


Result = Union[Ok[T], Err[E]]


def ok(value: T) -> Ok[T]:
    return Ok(value)


def err(error: E) -> Err[E]:
    return Err(error)
