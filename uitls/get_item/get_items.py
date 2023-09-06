import random
import string
import time


async def get_time() -> int:
    return int(time.time() * 1000)


async def get_ctoken() -> str:
    chars = string.ascii_lowercase + string.digits
    char = ''.join(random.choices(chars, k=370))
    return char
