from typing import Any

import httpx
from loguru import logger

from uitls.config.config import URL
from uitls.get_item.get_items import get_ctoken, get_time


async def make_request(url: str, data: dict, headers: dict) -> Any | None:
    async with httpx.AsyncClient() as client:
        response = await client.post(url=url, headers=headers, data=data)
        try:
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            logger.error(f"请求失败: {exc}")
            return None


async def learn_news_or_videos(endpoint: str, data: dict, headers: dict):
    response_data = await make_request(endpoint, data, headers)
    if response_data is not None:
        success = response_data.get('success', '')
        logger.success(f"{data.get('projectName', '')} 学习成功! 状态:{success}")


async def learn_news(title: str, project_id: str, headers: dict):
    data = {"projectName": title, "projectId": project_id}
    await learn_news_or_videos(endpoint=URL.LEARN_NEWS_URL, data=data, headers=headers)


async def learn_history_videos(project_id: int, headers: dict):
    data = {"projectId": project_id, "ctoken": await get_ctoken()}
    await learn_news_or_videos(URL.LEARN_VIDEO_HISTORY_URL.format(time=await get_time()), data, headers=headers)


async def learn_new_videos(headers: dict):
    data = {"ctoken": await get_ctoken(), "captchaId": '', "imgTrack": "{}"}
    await learn_news_or_videos(URL.LEARN_VIDEO_NEW_URL.format(time=await get_time()), data, headers=headers)
