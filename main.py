import asyncio
from typing import Tuple, List, Any

import uitls.database.db as db
from uitls.config.headers import headers
from uitls.get_item.get_list import UnlearnedList
from uitls.learning import learn_history_videos, learn_new_videos, learn_news


async def fetch_all_content() -> tuple[list, list]:
    """
    读取数据库中news videos表单的所有内容。
    """
    all_news = await db.get_all_news()
    all_videos = await db.get_all_videos()

    return all_news, all_videos


async def fetch_unlearned_content(user_id: str) -> tuple[list[Any], list[Any]]:
    """
    读取用户表单下的news 和 videos，并确定用户的数据与服务器的差异。
    """
    return await db.get_unlearned_content(user_id)


async def update_content(data_list: list, content_type: str):
    """
    更新videos news表单中的内容。
    """
    if content_type == "news":
        await db.insert_news(data_list)
    elif content_type == "videos":
        await db.insert_videos(data_list)


async def update_user_content(user_id: str, content_type: str, content_list: list):
    """
    更新用户表单下已学习过的内容
    """
    await db.update_user_learned_content(user_id, content_type, content_list)


async def get_and_update_list():
    unlearned_list = UnlearnedList(5)

    # 并发获取从unlearned_list的新闻和视频数据
    news_task = asyncio.create_task(unlearned_list.get_unlearned_news_list())
    videos_task = asyncio.create_task(unlearned_list.get_unlearned_videos_list())
    unlearned_news_list = await news_task
    unlearned_videos_list = await videos_task

    # 获取数据库中所有的news和videos数据
    all_news, all_videos = await fetch_all_content()

    # 判断unlearned_list数据中哪些内容数据库中不存在
    new_news = [news for news in unlearned_news_list if news not in all_news]
    new_videos = [video for video in unlearned_videos_list if video not in all_videos]

    # 并发更新数据库中不存在的新闻和视频内容
    if new_news:
        await update_content(data_list=new_news, content_type="news")
    if new_videos:
        await update_content(data_list=new_videos, content_type="videos")


async def auto_learn():
    all_user_ids = await db.fetch_all_user_ids()
    for user_id in all_user_ids:
        unlearned_news_list, unlearned_videos_list = await fetch_unlearned_content(user_id)
        # 提取news数组中的id和title
        news_ids, news_titles = [item["id"] for item in unlearned_news_list], [item["title"] for item in unlearned_news_list]
        for news_id, news_title in news_ids, news_titles:
            await learn_news(title=news_title, project_id=news_id, headers=await db.get_user_headers(user_id=user_id))
        # 提取videos数组中的project_id
        videos_project_ids = [item["project_id"] for item in unlearned_videos_list]
        # 需要鉴别周
        for videos_project_id in videos_project_ids:
            await learn_history_videos(videos_project_id)


async def main():
    user_id = "Cloxl"

    # 读取所有内容
    all_news, all_videos = await fetch_all_content()
    print(f"All News: {all_news}")
    print(f"All Videos: {all_videos}")

    # 读取未学习的内容
    unlearned_news, unlearned_videos = await fetch_unlearned_content(user_id)
    print(f"Unlearned News: {unlearned_news}")
    print(f"Unlearned Videos: {unlearned_videos}")

    # 更新内容
    new_news_data = [('new_id', 'new_title')]
    new_videos_data = [('new_project_id', 'new_img_id')]
    await update_content(new_news_data, "news")
    await update_content(new_videos_data, "videos")

    # 更新用户已学习的内容
    learned_news = ['new_id']
    learned_videos = ['new_project_id']
    await update_user_content(user_id, "news", learned_news)
    await update_user_content(user_id, "videos", learned_videos)
