import asyncio
from urllib.parse import urlparse

import aiohttp
from loguru import logger

from utils.config.config import URL, Time
from utils.get_item.get_items import get_time


class UnlearnedList:
    def __init__(self, max_page_count):
        self.max_page_count = max_page_count

    async def get_unlearned_news_list(self, headers: dict):
        unlearned_list_news = []
        async with aiohttp.ClientSession() as session:
            for page_count in range(self.max_page_count + 1):
                try:
                    url = URL.GET_NEWS_LIST_URL.format(time=await get_time())
                    data = {"page": page_count, "pageSize": 10, "reqType": "list"} if page_count > 0 else {}
                    response = await session.post(url=url, headers=headers, data=data)
                    logger.info(f"获取湖南青年说列表成功，当前是第{page_count + 1}页，状态:{response.status}")
                    if response.status == 200:
                        json_data = await response.json()
                        data_list = json_data.get('data', {}).get('list', [])
                        unlearned_list_news.extend([{'id': str(item.get('id', '')), 'title': item.get('title', '')}
                                                    for item in data_list])
                    await asyncio.sleep(Time.Sleep_time)
                except Exception as e:
                    logger.error(f"获取湖南青年说列表时出现错误，页数：{page_count + 1}。错误信息：{str(e)}")
        return unlearned_list_news

    async def get_unlearned_videos_list(self, headers: dict):
        unlearned_list_videos = []
        async with aiohttp.ClientSession() as session:
            for page_count in range(self.max_page_count + 1):
                try:
                    url = URL.GET_VIDEOS_LIST_URL.format(time=await get_time())
                    data = {"page": page_count, "pageSize": 10} if page_count > 0 else {}
                    response = await session.post(url=url, headers=headers, data=data)
                    logger.info(f"获取湖南大学习列表成功，当前是第{page_count + 1}页，状态:{response.status}")
                    if response.status == 200:
                        json_data = await response.json()
                        data_list = json_data.get('data', {}).get('list', [])
                        for item in data_list:
                            full_url = item.get('url', '')
                            parsed_url = urlparse(full_url)
                            unique_id = parsed_url.path.split('/')[-2]
                            unlearned_list_videos.append({'project_id': unique_id, 'img_id': full_url})
                    await asyncio.sleep(Time.Sleep_time)
                except Exception as e:
                    logger.error(f"获取湖南大学习列表时出现错误，页数：{page_count + 1}。错误信息：{str(e)}")
        return unlearned_list_videos

    async def get_learned_list(self, headers: dict):
        news, videos, history = [], [], []
        async with aiohttp.ClientSession() as session:
            for page_count in range(self.max_page_count + 1):
                try:
                    url = URL.GET_LEARNED_LIST_URL.format(time=await get_time())
                    data = {'page': page_count, 'pageSize': 20 if page_count == 0 else 10}
                    response = await session.post(url=url, headers=headers, data=data)
                    logger.info(f"已学习列表获取成功, 页数:{page_count + 1}, 状态:{response.status}")
                    if response.status == 200:
                        json_data = await response.json()
                        data_list = json_data.get('data', {}).get('list', [])
                        for item in data_list:
                            raw_project_id = str(item.get('projectId', ''))
                            if raw_project_id.startswith('9900990'):
                                news.append(raw_project_id[-4:])
                            elif len(raw_project_id) == 3:
                                videos.append(raw_project_id)
                            else:
                                history.append(raw_project_id)
                    await asyncio.sleep(Time.Sleep_time)
                except Exception as e:
                    logger.error(f"获取已学习列表时出现错误，页数：{page_count + 1}。错误信息：{str(e)}")
        return news, videos, history
