import asyncio

from bin.pygdo import launcher

if __name__ == '__main__':
    asyncio.run(launcher('$launch --force=1'))
