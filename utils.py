import time


def sleep_with_stop(total_seconds, stop_event, chunk=0.25):
    """
    Sleep in small chunks so a stop_event can interrupt lengthy waits.
    """
    elapsed = 0.0
    while elapsed < total_seconds and not stop_event.is_set():
        wait = min(chunk, total_seconds - elapsed)
        time.sleep(wait)
        elapsed += wait
