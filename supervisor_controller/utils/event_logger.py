from datetime import datetime
import sys
import traceback


class EventLogger:

    @staticmethod
    def log(msg: str, prefix: str = None, exc: Exception = None):
        dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if prefix:
            text = f'[{dt}] [{prefix}] {msg}'
        else:
            text = f'[{dt}] {msg}'

        print(text, file=sys.stderr, flush=True)

        if exc:
            print(f'[{dt}] [TRACEBACK]', file=sys.stderr, flush=True)
            traceback.print_exception(type(exc), exc, exc.__traceback__, file=sys.stderr, chain=False)
