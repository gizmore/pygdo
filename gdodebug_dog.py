import asyncio

import nest_asyncio

from bin.pygdo import launcher

if __name__ == '__main__':
    nest_asyncio.apply()
    asyncio.run(launcher('$launch --force=1'))
