# core/retry_handler.py
# Async-aware retry helper that can accept async callables.

import asyncio
import time
import traceback
from core.utils import get_logger

log = get_logger()

async def retry_action(action, attempts=3, delay=2, action_name="operation", fatal_exceptions=(), backoff=True, on_fail=None):
    """
    Retry wrapper that accepts either async or sync action.
    action: callable or coroutine function with no args.
    """
    last_exc = None
    for attempt in range(1, attempts+1):
        try:
            log.debug(f"[retry_action] Attempt {attempt}/{attempts} for {action_name}")
            result = action()
            if asyncio.iscoroutine(result):
                result = await result
            return result
        except fatal_exceptions as fe:
            log.error(f"[retry_action] Fatal exception: {fe}")
            raise
        except Exception as e:
            last_exc = e
            tb = traceback.format_exc(limit=1)
            log.warning(f"[retry_action] {action_name} failed (attempt {attempt}/{attempts}): {e}\n{tb}")
            if attempt == attempts:
                break
            sleep_for = delay * (2 ** (attempt-1)) if backoff else delay
            await asyncio.sleep(sleep_for)
    log.error(f"[retry_action] {action_name} permanently failed after {attempts} attempts.")
    if on_fail:
        try:
            on_fail(last_exc)
        except Exception as e:
            log.warning(f"[retry_action] on_fail callback raised: {e}")
    raise last_exc
