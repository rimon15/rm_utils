import asyncio
import inspect
from unittest.mock import Mock, call

import rimutil.timer as timer_module
from rimutil import Timer


def test_timer_context_prints_logs_and_writes_file(tmp_path, capsys, monkeypatch) -> None:
  logger = Mock()
  log_file = tmp_path / "timings.log"
  perf_counter_values = iter([10.0, 10.25])
  monkeypatch.setattr(timer_module.time, "perf_counter", lambda: next(perf_counter_values))

  with Timer(desc="load_data", fpath=str(log_file), logger=logger):
    pass

  captured = capsys.readouterr()
  assert captured.out == "load_data took: 0.250000 seconds\n"
  logger.info.assert_called_once_with("load_data took: 0.250000 seconds")
  assert log_file.read_text() == "load_data:\t0.250000\n"


def test_timer_decorator_uses_function_name_and_preserves_metadata(monkeypatch) -> None:
  logger = Mock()
  perf_counter_values = iter([20.0, 20.1, 30.0, 30.2])
  monkeypatch.setattr(timer_module.time, "perf_counter", lambda: next(perf_counter_values))

  @Timer(logger=logger, do_print=False)
  def compute(value: int) -> int:
    return value * 2

  assert compute(2) == 4
  assert compute(3) == 6
  assert compute.__name__ == "compute"
  assert logger.info.call_args_list == [
    call("compute took: 0.100000 seconds"),
    call("compute took: 0.200000 seconds"),
  ]


def test_timer_async_context_prints_logs_and_writes_file(tmp_path, capsys, monkeypatch) -> None:
  logger = Mock()
  log_file = tmp_path / "async_timings.log"
  perf_counter_values = iter([40.0, 40.25])
  monkeypatch.setattr(timer_module.time, "perf_counter", lambda: next(perf_counter_values))

  async def run() -> Timer:
    async with Timer(desc="fetch_data", fpath=str(log_file), logger=logger) as timer:
      await asyncio.sleep(0)
    return timer

  timer = asyncio.run(run())

  captured = capsys.readouterr()
  assert captured.out == "fetch_data took: 0.250000 seconds\n"
  assert timer.elapsed == 0.25
  logger.info.assert_called_once_with("fetch_data took: 0.250000 seconds")
  assert log_file.read_text() == "fetch_data:\t0.250000\n"


def test_timer_async_decorator_supports_concurrent_calls(monkeypatch) -> None:
  logger = Mock()
  perf_counter_values = iter([50.0, 60.0, 60.5, 61.0])
  monkeypatch.setattr(timer_module.time, "perf_counter", lambda: next(perf_counter_values))

  @Timer(logger=logger, do_print=False)
  async def work(name: str, ready: asyncio.Event, release: asyncio.Event) -> str:
    ready.set()
    await release.wait()
    return name

  async def run() -> tuple[str, str]:
    ready_one = asyncio.Event()
    ready_two = asyncio.Event()
    release_one = asyncio.Event()
    release_two = asyncio.Event()

    task_one = asyncio.create_task(work("first", ready_one, release_one))
    task_two = asyncio.create_task(work("second", ready_two, release_two))

    await ready_one.wait()
    await ready_two.wait()

    release_one.set()
    first = await task_one

    release_two.set()
    second = await task_two

    return first, second

  first, second = asyncio.run(run())

  assert (first, second) == ("first", "second")
  assert inspect.iscoroutinefunction(work)
  assert work.__name__ == "work"
  assert logger.info.call_args_list == [
    call("work took: 10.500000 seconds"),
    call("work took: 1.000000 seconds"),
  ]
