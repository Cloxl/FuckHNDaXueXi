import asyncio
from urllib.parse import urlparse

import httpx
from loguru import logger

from uitls.config.headers import headers
from uitls.config.URL import URL
from uitls.get_item.get_items import get_time


class UnlearnedList:
    def __init__(self, max_page_count):
        self.max_page_count = max_page_count

    async def get_unlearned_news_list(self):
        unlearned_list_news = []
        async with httpx.AsyncClient() as client:
            for page_count in range(self.max_page_count + 1):
                url = URL.GET_NEWS_LIST_URL.format(time=await get_time())
                data = {"page": page_count, "pageSize": 10, "reqType": "list"} if page_count > 0 else {}
                response = await client.post(url=url, headers=headers, data=data)
                logger.info(f"获取湖南青年说列表成功，当前是第{page_count + 1}页，状态:{response.status_code}")
                if response.status_code == 200:
                    json_data = response.json()
                    data_list = json_data.get('data', {}).get('list', [])
                    unlearned_list_news.extend([{'id': str(item.get('id', '')), 'title': item.get('title', '')}
                                                for item in data_list])
                await asyncio.sleep(1)
        return unlearned_list_news

    async def get_unlearned_videos_list(self):
        unlearned_list_videos = []
        async with httpx.AsyncClient() as client:
            for page_count in range(self.max_page_count + 1):
                url = URL.GET_VIDEOS_LIST_URL.format(time=await get_time())
                data = {"page": page_count, "pageSize": 10} if page_count > 0 else {}
                response = await client.post(url=url, headers=headers, data=data)
                logger.info(f"获取湖南大学习列表成功，当前是第{page_count + 1}页，状态:{response.status_code}")
                if response.status_code == 200:
                    json_data = response.json()
                    data_list = json_data.get('data', {}).get('list', [])
                    for item in data_list:
                        full_url = item.get('url', '')
                        parsed_url = urlparse(full_url)
                        unique_id = parsed_url.path.split('/')[-2]
                        unlearned_list_videos.append({'project_id': unique_id, 'img_id': full_url})
                await asyncio.sleep(1)
        return unlearned_list_videos

    async def get_learned_list(self):
        news, videos, history = [], [], []
        async with httpx.AsyncClient() as client:
            for page_count in range(self.max_page_count + 1):
                url = URL.GET_LEARNED_LIST_URL.format(time=await get_time())
                data = {'page': page_count, 'pageSize': 20 if page_count == 0 else 10}
                response = await client.post(url=url, headers=headers, data=data)
                logger.info(f"已学习列表获取成功, 页数:{page_count + 1}, 状态:{response.status_code}")
                if response.status_code == 200:
                    json_data = response.json()
                    data_list = json_data.get('data', {}).get('list', [])
                    for item in data_list:
                        raw_project_id = str(item.get('projectId', ''))
                        if raw_project_id.startswith('9900990'):
                            news.append(raw_project_id[-4:])
                        elif len(raw_project_id) == 3:
                            videos.append(raw_project_id)
                        else:
                            history.append(raw_project_id)
                await asyncio.sleep(1)
        return news, videos, history

# async def main():
#     max_page_count = 5  # 你可以根据需要设置最大页数
#     obj = UnlearnedList(max_page_count)
#     news_list = await obj.get_unlearned_news_list()
#     videos_list = await obj.get_unlearned_videos_list()
#     learned_list = await obj.get_learned_list()
#     print("未学习新闻列表:", news_list)
#     print("未学习视频列表:", videos_list)
#     print("已学习列表:", learned_list)
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
