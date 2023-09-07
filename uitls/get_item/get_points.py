import re

import aiohttp
from loguru import logger

from uitls.config.config import URL
from uitls.config.headers import headers


async def get_points():
    try:
        async with aiohttp.ClientSession() as session:
            response = await session.get(URL.GET_POINT_URL, headers=headers)
            if response.status == 200:
                match = re.search(r"积分：(\\d+)分", await response.text())
                if match:
                    logger.info(f"积分获取成功，状态:{response.status}")
                    return match.group(1)
    except Exception as e:
        logger.error(f"获取积分时出现错误。错误信息：{str(e)}")
    return None
