import sys
import traceback


class Logger:

    @classmethod
    def debug(cls, s: str):
        print(f"{s}")

    @classmethod
    def exception(cls, ex: Exception):
        sys.stderr.write(str(ex))
        sys.stderr.write(traceback.format_exc())
