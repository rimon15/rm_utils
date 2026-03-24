import inspect
import time
from collections.abc import Awaitable, Callable
from functools import wraps
from os import PathLike
from typing import Any, ParamSpec, Protocol, Self, TypeVar, overload


P = ParamSpec("P")
R = TypeVar("R")


class SupportsInfo(Protocol):
  def info(self, message: str, *args: object, **kwargs: object) -> object: ...


class Timer:
  def __init__(
    self,
    desc: str = "",
    fpath: str | PathLike[str] | None = None,
    logger: SupportsInfo | None = None,
    do_print: bool = True,
  ):
    self.desc = desc
    self.fpath = fpath
    self.logger = logger
    self.do_print = do_print
    self.start_time: float | None = None
    self.elapsed: float | None = None

  def _get_desc(self, fallback: str) -> str:
    return self.desc or fallback

  def _new_timer(self, fallback: str) -> Self:
    return type(self)(
      desc=self._get_desc(fallback),
      fpath=self.fpath,
      logger=self.logger,
      do_print=self.do_print,
    )

  def _emit(self, elapsed: float, fallback: str) -> None:
    desc = self._get_desc(fallback)
    message = f"{desc} took: {elapsed:.6f} seconds"

    if self.do_print:
      print(message)
    if self.logger is not None:
      self.logger.info(message)
    if self.fpath is not None:
      with open(self.fpath, "a", encoding="utf-8") as f:
        f.write(f"{desc}:\t{elapsed:.6f}\n")

  def _start(self) -> Self:
    self.start_time = time.perf_counter()
    self.elapsed = None
    return self

  def _stop(self, fallback: str) -> None:
    if self.start_time is None:
      raise RuntimeError("Timer has not been started")
    self.elapsed = time.perf_counter() - self.start_time
    self._emit(self.elapsed, fallback=fallback)

  def __enter__(self) -> Self:
    return self._start()

  def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
    self._stop(fallback="block")
    return False

  async def __aenter__(self) -> Self:
    return self._start()

  async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
    self._stop(fallback="block")
    return False

  @overload
  def __call__(self, func: Callable[P, R]) -> Callable[P, R]: ...

  @overload
  def __call__(self, func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]: ...

  def __call__(self, func: Callable[P, Any]) -> Callable[P, Any]:
    if inspect.iscoroutinefunction(func):

      @wraps(func)
      async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
        async with self._new_timer(func.__name__):
          return await func(*args, **kwargs)

      return async_wrapper

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
      with self._new_timer(func.__name__):
        return func(*args, **kwargs)

    return wrapper
