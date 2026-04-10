from importlib import import_module


def enable_lovely_tensors() -> None:
  try:
    lovely_tensors = import_module("lovely_tensors")
  except ImportError:
    return

  lovely_tensors.monkey_patch()
