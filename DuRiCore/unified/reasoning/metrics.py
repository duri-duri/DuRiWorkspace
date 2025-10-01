from contextlib import contextmanager
import time


@contextmanager
def timer():
    t0 = time.perf_counter()
    yield lambda: time.perf_counter() - t0
