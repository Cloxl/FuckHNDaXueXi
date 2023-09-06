import json
from typing import Tuple, List, Any
import aiosqlite

DB_NAME = 'utils/database/main.db'


async def init_db():
    """
    初始化数据库，创建所需的表。
    """
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.cursor()

        # Create the news table
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS news (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL
            );
        """)

        # Create the videos table
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                project_id TEXT PRIMARY KEY,
                img_id TEXT NOT NULL
            );
        """)

        # Create the user table
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                headers TEXT,
                learned_news TEXT,
                learned_videos TEXT
            );
        """)

        await db.commit()


async def insert_news(data_list: list[dict]):
    """
    插入新闻数据到news表中。

    参数:
        data_list (list[dict]): 新闻数据列表。
    """
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.cursor()
        values = [(item['id'], item['title']) for item in data_list]
        await cursor.executemany("INSERT OR IGNORE INTO news (id, title) VALUES (?, ?)", values)
        await db.commit()


async def insert_videos(data_list: list[dict]):
    """
    插入视频数据到videos表中。

    参数:
        data_list (list[dict]): 视频数据列表。
    """
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.cursor()
        values = [(item['project_id'], item['img_id']) for item in data_list]
        await cursor.executemany("INSERT OR IGNORE INTO videos (project_id, img_id) VALUES (?, ?)", values)
        await db.commit()


async def insert_user(uid: str, headers: dict, last_history: list):
    """
    插入用户数据到user表中。

    参数:
        uid (str): 用户ID。
        headers (dict): 用户的headers。
        last_history (list): 用户的最后浏览历史。
    """
    headers_str = json.dumps(headers)
    last_history_str = json.dumps(last_history)
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.cursor()
        await cursor.execute("INSERT INTO user (uid, user_headers, user_last_history) VALUES (?, ?, ?)",
                             (uid, headers_str, last_history_str))
        await db.commit()


async def get_user_headers(user_id: str) -> dict:
    """
    从数据库中根据用户ID获取用户的headers。

    参数:
        user_id (str): 用户ID。

    返回:
        dict: 用户的headers。
    """
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.cursor()
        await cursor.execute("SELECT headers FROM user WHERE rowid = ?", (user_id,))
        result = await cursor.fetchone()
        if result:
            return json.loads(result[0])
        return {}


async def update_user_learned_content(user_id: str, content_type: str, content_list: list[dict]):
    """
    更新用户已学习的内容。

    参数:
        user_id (str): 用户ID。
        content_type (str): 内容类型，可以是"news"或"videos"。
        content_list (list[dict]): 用户已学习的内容列表。
    """
    content_str = ",".join([str(item['id']) for item in content_list])
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.cursor()
        if content_type == "news":
            await cursor.execute("UPDATE user SET learned_news = ? WHERE rowid = ?", (content_str, user_id))
        elif content_type == "videos":
            await cursor.execute("UPDATE user SET learned_videos = ? WHERE rowid = ?", (content_str, user_id))
        await db.commit()


async def get_all_news() -> list[dict]:
    """
    从数据库中获取所有新闻。

    返回:
        list[dict]: 包含所有新闻的列表。
    """
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.cursor()
        await cursor.execute("SELECT id, title FROM news")
        result = await cursor.fetchall()
        return [{"id": item[0], "title": item[1]} for item in result]


async def get_all_videos() -> list[dict]:
    """
       从数据库中获取所有视频。

       返回:
           list[dict]: 包含所有视频的列表。
       """
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.cursor()
        await cursor.execute("SELECT project_id, img_id FROM videos")
        result = await cursor.fetchall()
        return [{"project_id": item[0], "img_id": item[1]} for item in result]


async def get_user_learned_content(user_id: str) -> Tuple[List[dict], List[dict]]:
    """
       根据用户ID从数据库中获取用户已学习的新闻和视频。

       参数:
           user_id (str): 用户ID。

       返回:
           Tuple[List[dict], List[dict]]: 第一个列表是用户已学习的新闻，第二个列表是用户已学习的视频。
       """
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.cursor()
        await cursor.execute("SELECT learned_news, learned_videos FROM user WHERE rowid = ?", (user_id,))
        result = await cursor.fetchone()
        if result:
            learned_news_ids = result[0].split(",") if result[0] else []
            learned_videos_ids = result[1].split(",") if result[1] else []

            # 获取用户已经读取news数量
            await cursor.execute("SELECT id, title FROM news WHERE id IN ({})".format(",".join("?" * len(learned_news_ids))), learned_news_ids)
            news_result = await cursor.fetchall()
            learned_news = [{"id": item[0], "title": item[1]} for item in news_result]

            # 获取用户已经读取的videos数量
            await cursor.execute("SELECT project_id, img_id FROM videos WHERE project_id IN ({})".format(",".join("?" * len(learned_videos_ids))), learned_videos_ids)
            videos_result = await cursor.fetchall()
            learned_videos = [{"project_id": item[0], "img_id": item[1]} for item in videos_result]

            return learned_news, learned_videos
        return [], []


async def get_unlearned_content(user_id: str) -> tuple[list[Any], list[Any]]:
    """
        根据用户ID从数据库中获取用户未学习的新闻和视频。

        参数:
            user_id (str): 用户ID。

        返回:
            tuple[list[Any], list[Any]]: 第一个列表是用户未学习的新闻，第二个列表是用户未学习的视频。
        """
    learned_news, learned_videos = await get_user_learned_content(user_id)
    all_news = await get_all_news()
    all_videos = await get_all_videos()

    unlearned_news = [news for news in all_news if news not in learned_news]
    unlearned_videos = [video for video in all_videos if video not in learned_videos]

    return unlearned_news, unlearned_videos


async def fetch_all_user_ids() -> List[str]:
    """
    从数据库中获取所有用户的uid。
    """
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.cursor()
        await cursor.execute("SELECT rowid FROM user")
        result = await cursor.fetchall()
        return [str(item[0]) for item in result]


async def add_learned_news(uid: str, news_id: str):
    """
    将已学习的新闻ID添加到user_learned_news表中。

    参数:
        uid (str): 用户ID。
        news_id (str): 已学习的新闻ID。
    """
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.cursor()
        await cursor.execute("INSERT INTO user_learned_news (uid, news_id) VALUES (?, ?)", (uid, news_id))
        await db.commit()


async def remove_learned_news(uid: str, news_id: str):
    """
    从user_learned_news表中删除已学习的新闻ID。

    参数:
        uid (str): 用户ID。
        news_id (str): 已学习的新闻ID。
    """
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.cursor()
        await cursor.execute("DELETE FROM user_learned_news WHERE uid = ? AND news_id = ?", (uid, news_id))
        await db.commit()


async def add_learned_video(uid: str, video_id: str):
    """
    将已学习的视频ID添加到user_learned_videos表中。

    参数:
        uid (str): 用户ID。
        video_id (str): 已学习的视频ID。
    """
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.cursor()
        await cursor.execute("INSERT INTO user_learned_videos (uid, video_id) VALUES (?, ?)", (uid, video_id))
        await db.commit()


async def remove_learned_video(uid: str, video_id: str):
    """
    从user_learned_videos表中删除已学习的视频ID。

    参数:
        uid (str): 用户ID。
        video_id (str): 已学习的视频ID。
    """
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.cursor()
        await cursor.execute("DELETE FROM user_learned_videos WHERE uid = ? AND video_id = ?", (uid, video_id))
        await db.commit()


async def update_user_headers(uid: str, headers: dict):
    """
    更新user表中的headers字段。

    参数:
        uid (str): 用户ID。
        headers (dict): 新的headers数据。
    """
    headers_str = json.dumps(headers)
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.cursor()
        await cursor.execute("UPDATE user SET user_headers = ? WHERE uid = ?", (headers_str, uid))
        await db.commit()


async def update_user_last_history(uid: str, last_history: list):
    """
    更新user表中的user_last_history字段。

    参数:
        uid (str): 用户ID。
        last_history (list): 新的浏览历史数据。
    """
    last_history_str = json.dumps(last_history)
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.cursor()
        await cursor.execute("UPDATE user SET user_last_history = ? WHERE uid = ?", (last_history_str, uid))
        await db.commit()
