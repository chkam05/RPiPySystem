from datetime import datetime
import sys
import traceback


class EventLogger:

    @staticmethod
    def log(msg: str, prefix: str = None, exc: Exception = None):
        """
        Universal log output. Safe for supervisor listeners (uses stderr).
        Automatically timestamps and flushes immediately.

        :param msg: Text message to log
        :param prefix: Optional tag (e.g. 'reaper', 'nginx_stop')
        :param exc: Optional exception to include traceback for
        """
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if prefix:
            text = f'[{ts}] [{prefix}] {msg}'
        else:
            text = f'[{ts}] {msg}'

        print(text, file=sys.stderr, flush=True)

        if exc:
            print(f'[{ts}] [TRACEBACK]', file=sys.stderr, flush=True)
            traceback.print_exception(type(exc), exc, exc.__traceback__, file=sys.stderr, chain=False)
