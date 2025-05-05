import sys

from gdo.base.Application import Application
from gdo.core.Cronjob import Cronjob


if __name__ == '__main__':
    Application.init(__file__ + "/../")
    Cronjob.run(True)
