import re

import httpx
from loguru import logger

from uitls.config.headers import headers
from uitls.config.URL import URL


async def get_points():
    async with httpx.AsyncClient() as client:
        response = await client.get(URL.GET_POINT_URL, headers=headers)
        if response.status_code == 200:
            match = re.search(r"积分：(\d+)分", response.text)
            if match:
                logger.info(f"积分获取成功，状态:{response.status_code}")
                return match.group(1)
    return None
