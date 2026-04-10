import importlib
from unittest.mock import Mock

import rimutil
import rimutil._lovely as lovely_module


def test_enable_lovely_tensors_calls_monkey_patch(monkeypatch) -> None:
  fake_lovely_tensors = Mock()
  monkeypatch.setattr(lovely_module, "import_module", lambda name: fake_lovely_tensors)

  lovely_module.enable_lovely_tensors()

  fake_lovely_tensors.monkey_patch.assert_called_once_with()


def test_enable_lovely_tensors_is_optional(monkeypatch) -> None:
  def raise_import_error(name: str) -> None:
    raise ImportError(name)

  monkeypatch.setattr(lovely_module, "import_module", raise_import_error)

  lovely_module.enable_lovely_tensors()


def test_importing_rimutil_enables_lovely_tensors(monkeypatch) -> None:
  enable_lovely_tensors = Mock()
  monkeypatch.setattr(lovely_module, "enable_lovely_tensors", enable_lovely_tensors)

  importlib.reload(rimutil)

  enable_lovely_tensors.assert_called_once_with()
