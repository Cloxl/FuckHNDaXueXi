import aiohttp
import asyncio
from loguru import logger

from urllib.parse import quote
from uitls.config.headers import headers
from uitls.config.URL import URL


async def get_imgs(img_id: str):
    async with aiohttp.ClientSession() as session:
        logger.info(URL.GET_IMAGE_URL.format(img_id))
        url = URL.GET_IMAGE_URL.format(quote(img_id))
        async with session.get(url=url, headers=headers) as response:
            if response.status == 200:
                with open(f"imgs/{img_id}.jpg", "wb") as f:
                    f.write(await response.read())
            else:
                logger.error(f"请求失败: {response.status}")
                return None

if __name__ == '__main__':
    asyncio.run(get_imgs("oadrpgvnys"))
