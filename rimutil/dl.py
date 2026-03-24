import gc
import random

try:
  import numpy as np
  import torch
except ImportError as exc:
  raise ImportError(
    "rimutil.dl requires the optional 'dl' dependencies. "
    "Install them with `pip install rimutil[dl]`."
  ) from exc


def seed_all(seed: int) -> None:
  random.seed(seed)
  np.random.seed(seed)
  torch.manual_seed(seed)

  if torch.cuda.is_available():
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

  torch.backends.cudnn.deterministic = True
  torch.backends.cudnn.benchmark = False


def cleanup_gpu_mem() -> None:
  gc.collect()

  if torch.cuda.is_available():
    torch.cuda.empty_cache()


def cleanup_gpu_memory() -> None:
  cleanup_gpu_mem()


__all__ = ["seed_all", "cleanup_gpu_mem", "cleanup_gpu_memory"]
