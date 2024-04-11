
class Logger:

    @classmethod
    def debug(cls, s: str):
        print(f"{s}")

    @classmethod
    def exception(cls, ex: Exception):
        print(ex)
