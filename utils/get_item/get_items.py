import json
import re
import subprocess
import time

import aiohttp
import execjs
from loguru import logger

from utils.config.config import URL


async def get_time() -> int:
    return int(time.time() * 1000)


async def get_token(token: str, pubkeySM2: str) -> str:
    with open('./static/encrypt.js', 'r') as file:
        js_code = file.read()

    context = execjs.compile(js_code)
    encrypted_token = context.call('encrypt', token, pubkeySM2, 0)
    return encrypted_token


async def get_points_or_token(headers: dict, get_type: str) -> str:
    type_label = None
    try:
        async with aiohttp.ClientSession() as session:
            response = await session.get(URL.GET_POINT_URL, headers=headers)
            if response.status == 200:
                type_label = "积分" if get_type == 'point' else "token" if get_type == 'token' else None
                if type_label is None:
                    return "输入类型有误"

                if get_type == 'point':
                    match = re.search(r"积分：(\d+)分", await response.text())
                elif get_type == 'token':
                    match = re.search(r":submitStudy20\('([^']+)'\)", await response.text())

                if match:
                    logger.info(f"{type_label}获取成功，状态:{response.status}, {type_label}:{match.group(1)}")
                    return match.group(1)
                else:
                    logger.info(f"未找到有效的{type_label}")
            else:
                logger.info("HTTP 请求未成功")
    except Exception as e:
        logger.error(f"获取{type_label}时出现错误, 错误信息：{str(e)}")
        return f"获取{type_label}出现错误"

    return "未知错误"

