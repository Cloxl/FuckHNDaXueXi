import asyncio
import random
from typing import Any

from loguru import logger

import utils.database.db as db
from utils.get_item.get_list import UnlearnedList
from utils.learning import learn_history_videos, learn_news


async def fetch_all_content() -> tuple[list, list]:
    """
    读取数据库中news videos表单的所有内容。
    """
    try:
        all_news = await db.get_all_news()
        all_videos = await db.get_all_videos()
        return all_news, all_videos
    except Exception as e:
        logger.error(f"读取所有内容出错: {e}")
        return [], []


async def fetch_unlearned_content(user_id: str) -> tuple[list[Any], list[Any]]:
    """
    读取用户表单下的news 和 videos，并确定用户的数据与服务器的差异。
    """
    try:
        return await db.get_unlearned_content(user_id)
    except Exception as e:
        logger.error(f"读取未学习内容出错，用户ID：{user_id}. 错误信息: {e}")
        return [], []


async def update_content(data_list: list, content_type: str):
    """
    更新videos news表单中的内容。
    """
    try:
        if content_type == "news":
            await db.insert_news(data_list)
        elif content_type == "videos":
            await db.insert_videos(data_list)
    except Exception as e:
        logger.error(f"更新{content_type}内容出错. 错误信息: {e}")


async def update_user_content(user_id: str, content_type: str, content_list: list):
    """
    更新用户表单下已学习过的内容
    """
    try:
        await db.update_user_learned_content(user_id, content_type, content_list)
    except Exception as e:
        logger.error(f"更新用户{user_id}的{content_type}内容出错. 错误信息: {e}")


async def auto_update_list(uid: str = "auto"):
    """
    自动更新大学习任务

    参数:
        uid (str): 用户ID， 默认auto 即随机挑选一个用户
    """
    unlearned_list = UnlearnedList(5)
    headers = None
    if uid != "auto":
        try:
            headers = await db.get_user_headers(user_id=uid)
            logger.info(f"获取指定用户 {uid} 的请求头成功!")
        except Exception as e:
            logger.error(f"获取指定用户 {uid} 的请求头失败 原因:{e}")
    else:
        try:
            headers = await db.get_user_headers(random.choice(await db.fetch_all_user_ids()))
            logger.info(f"成功获取随级请求头")
        except IndexError:
            # 处理没有用户的情况
            logger.warning("没有任何用户存在数据库，自动暂停更新列表程序")
            return

    try:
        if headers is None:
            logger.error("请求头未定义 不能继续执行")
            return
        # 并发获取从unlearned_list的新闻和视频数据
        news_task = asyncio.create_task(unlearned_list.get_unlearned_news_list(headers=headers))
        videos_task = asyncio.create_task(unlearned_list.get_unlearned_videos_list(headers=headers))
        unlearned_news_list = await news_task
        unlearned_videos_list = await videos_task
        logger.info(f"成功获取unlearned_list的新闻和视频数据")
    except Exception as e:
        logger.error(f"获取unlearned_list发生错误: {e}")
        return

    try:
        # 获取数据库中所有的news和videos数据
        all_news, all_videos = await fetch_all_content()
        logger.info("成功获取数据库内的所有news videos数据")
    except Exception as e:
        logger.error(f"获取数据库中的news videos发生错误: {e}")
        return

    # 判断unlearned_list数据中哪些内容数据库中不存在
    new_news = [news for news in unlearned_news_list if news not in all_news]
    new_videos = [video for video in unlearned_videos_list if video not in all_videos]

    # 并发更新数据库中不存在的新闻和视频内容
    if new_news:
        await update_content(data_list=new_news, content_type="news")
        logger.info(f"成功更新news数据库 更新数量{len(new_news)}")
    if new_videos:
        await update_content(data_list=new_videos, content_type="videos")
        logger.info(f"成功更新news数据库 更新数量{len(new_videos)}")


async def auto_learn(uid: str = "auto"):
    """
    自动学习未学习的大学习任务

    参数:
        uid (str): 用户ID， 默认auto 即所有用户
    """
    if uid != "auto":
        all_user_ids = [uid]
        logger.info(f"成功获取指定用户数据 {uid}")
    else:
        try:
            all_user_ids = await db.fetch_all_user_ids()
            logger.info(f"成功获取所有用户数据,当前用户量:{len(all_user_ids)}")
        except Exception as e:
            logger.error(f"获取所有用户失败: {e}")
            return

    for user_id in all_user_ids:
        await process_single_user_learning(user_id)


async def process_single_user_learning(user_id: str):
    try:
        headers = await db.get_user_headers(user_id=user_id)
        unlearned_news_list, unlearned_videos_list = await fetch_unlearned_content(user_id)
        if not unlearned_news_list or unlearned_videos_list:
            logger.warning(f"未获取任何用户 {user_id} 未学习的内容 可能用户已经学完了所有内容 ")
            return
        logger.info(f"获取用户 {user_id} 未学习列表成功")
    except Exception as e:
        logger.error(f"获取用户 {user_id} 未学习的列表失败，将自动跳过该用户，进入下一个用户: {e}")
        return

    # 提取news数组中的id和title
    news_ids, news_titles = [item["id"] for item in unlearned_news_list], [item["title"] for item in
                                                                           unlearned_news_list]
    for news_id, news_title in zip(news_ids, news_titles):
        try:
            await learn_news(title=news_title, project_id=news_id, headers=headers)
            logger.info(f"用户 {user_id} 学习湖南青年说成功 - {news_id}")
        except Exception as e:
            logger.error(f"学习{news_id} - {news_title}失败: {e}")

    # 提取videos数组中的project_id
    videos_project_ids = [item["project_id"] for item in unlearned_videos_list]
    try:
        # 访问数据库 看看这一周是否完成了 知识回顾
        history_list = await db.get_user_last_history(uid=user_id)
        logger.info(f"获取用户 {user_id} 往期回顾内容成功")
    except Exception as e:
        logger.error(f"用户{user_id}获取本周知识回顾失败: {e}")
        return

    # 如果小于5则知识回顾能加的分未达到上限 继续学习        如果大于等于5 这是不可能发生的 因为一周只能有5次知识回顾
    if len(history_list) < 5:
        for videos_project_id in videos_project_ids:
            try:
                await learn_history_videos(videos_project_id, headers=headers)
            except Exception as e:
                logger.error(f"用户{user_id}学习往期回顾{videos_project_id}失败: {e}")
    else:
        logger.warning(f"用户 {user_id} 本周已完成往期回顾任务")
