import json
from typing import Any

import aiohttp
from loguru import logger

from utils.config.config import URL
from utils.get_item.get_items import get_time, get_token


async def make_request(url: str, data: dict, headers: dict, is_new_video_mode: bool = False) -> Any | None:
    try:
        async with aiohttp.ClientSession() as session:
            response = await session.post(url=url, headers=headers, data=data)
            response.raise_for_status()

            try:
                return await response.json()
            except aiohttp.ContentTypeError:
                if is_new_video_mode:
                    content = await response.text()
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        logger.error(f"新视频模式下，JSON 解析失败，原内容: {content}")
                        return None
                else:
                    content = await response.text()
                    logger.error(f"JSON 解析失败，原内容: {content}")
                    return None
    except aiohttp.ClientError as e:
        logger.error(f"请求失败: {e}")
        return None


async def learn_news(title: str, project_id: str, headers: dict):
    data = {"projectName": title, "projectId": project_id}
    response_data = await make_request(url=URL.LEARN_NEWS_URL, data=data, headers=headers)
    if response_data is not None:
        success = response_data.get('success', '')
        logger.success(f"{title} 学习成功! 状态:{success}")


async def learn_history_videos(project_id: int, headers: dict, token: str, pubkeySM2: str):
    data = {"projectId": project_id, "ctoken": await get_token(token=token, pubkeySM2=pubkeySM2)}
    response_data = await make_request(url=URL.LEARN_VIDEO_HISTORY_URL.format(time=await get_time()), data=data,
                                       headers=headers)
    if response_data is not None:
        success = response_data.get('success', '')
        logger.success(f"历史视频学习成功! 项目ID: {project_id}, 状态:{success}")


async def learn_new_videos(headers: dict, token: str, pubkeySM2: str):
    data = {"ctoken": await get_token(token=token, pubkeySM2=pubkeySM2), "captchaId": '',
            "imgTrack": "{}"}
    # data = {"projectId": 162, "ctoken": await get_token(token=token, pubkeySM2=pubkeySM2), "captchaId": '',
    #         "imgTrack": "{}"}
    response_data = await make_request(url=URL.LEARN_VIDEO_NEW_URL.format(time=await get_time()), data=data,
                                       headers=headers, is_new_video_mode=True)
    if response_data is not None:
        success = response_data.get('success', '')
        logger.success(f"新视频学习成功! 状态:{success}")

    return response_data
