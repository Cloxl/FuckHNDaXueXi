import json
from typing import List, Tuple

import aiosqlite
import bcrypt
from loguru import logger

DB_NAME = 'utils/database/main.db'

# 使用连接池进行管理
connection_pool = 5


async def init_db():
    """
    初始化数据库，创建所需的表。
    """
    await execute("""
        CREATE TABLE IF NOT EXISTS news (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL
        );
    """)
    await execute("""
        CREATE TABLE IF NOT EXISTS videos (
            project_id TEXT PRIMARY KEY,
            img_id TEXT NOT NULL
        );
    """)
    await execute("""
        CREATE TABLE IF NOT EXISTS user (
            uid TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            headers TEXT NOT NULL,
            last_history TEXT NOT NULL
        );
    """)
    await execute("""
        CREATE TABLE IF NOT EXISTS user_learned_news (
            user_id TEXT,
            news_id TEXT,
            FOREIGN KEY (user_id) REFERENCES user(uid),
            FOREIGN KEY (news_id) REFERENCES news(id)
        );
    """)
    await execute("""
        CREATE TABLE IF NOT EXISTS user_learned_videos (
            user_id TEXT,
            video_id TEXT,
            FOREIGN KEY (user_id) REFERENCES user(uid),
            FOREIGN KEY (video_id) REFERENCES videos(project_id)
        );
    """)


async def get_connection():
    """
    获取连接池
    """
    global connection_pool
    if connection_pool is None:
        connection_pool = await aiosqlite.connect(DB_NAME, isolation_level=None)
    return connection_pool


async def close_connection():
    """
    关闭连接池
    """
    global connection_pool
    if connection_pool:
        await connection_pool.close()
        connection_pool = None


def handle_exception(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"功能异常 {func.__name__}: {str(e)}")
            raise e

    return wrapper


@handle_exception
async def execute(query: str, params: Tuple = None):
    db = await get_connection()
    async with db.cursor() as cursor:
        if params:
            await cursor.execute(query, params)
        else:
            await cursor.execute(query)
        await db.commit()


@handle_exception
async def fetch_one(query: str, params: Tuple = None):
    db = await get_connection()
    async with db.cursor() as cursor:
        if params:
            await cursor.execute(query, params)
        else:
            await cursor.execute(query)
        return await cursor.fetchone()


@handle_exception
async def fetch_all(query: str, params: Tuple = None):
    db = await get_connection()
    async with db.cursor() as cursor:
        if params:
            await cursor.execute(query, params)
        else:
            await cursor.execute(query)
        return await cursor.fetchall()


async def insert_news(data_list: list[dict]):
    query = "INSERT OR IGNORE INTO news (id, title) VALUES (?, ?)"
    values = [(item['id'], item['title']) for item in data_list]
    await execute(query, values)


async def get_user_headers(user_id: str) -> dict:
    query = "SELECT headers FROM user WHERE rowid = ?"
    result = await fetch_one(query, (user_id,))
    if result:
        return json.loads(result[0])
    return {}


async def add_learned_news(uid: str, news_id: str):
    query = "INSERT INTO user_learned_news (uid, news_id) VALUES (?, ?)"
    await execute(query, (uid, news_id))


async def insert_videos(data_list: list[dict]):
    query = "INSERT OR IGNORE INTO videos (project_id, img_id) VALUES (?, ?)"
    values = [(item['project_id'], item['img_id']) for item in data_list]
    await execute(query, values)


async def hash_password(pwd: str) -> str:
    """
    使用bcrypt哈希密码
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd.encode('utf-8'), salt)
    return hashed.decode('utf-8')


async def insert_user(uid: str, password: str, headers: dict, last_history: list):  # <-- 添加密码参数
    hashed_password = await hash_password(password)  # 使用bcrypt哈希密码
    headers_str = json.dumps(headers)
    last_history_str = json.dumps(last_history)
    await execute("INSERT INTO user (uid, password, headers, last_history) VALUES (?, ?, ?, ?)",  # <-- 插入哈希后的密码
                  (uid, hashed_password, headers_str, last_history_str))


async def check_password(hashed_password: str, user_password: str) -> bool:
    """
    检查用户提供的密码是否与哈希密码匹配。
    """
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password.encode('utf-8'))


async def add_learned_video(uid: str, video_id: str):
    query = "INSERT INTO user_learned_videos (user_id, video_id) VALUES (?, ?)"
    await execute(query, (uid, video_id))


async def remove_learned_news(uid: str, news_id: str):
    await execute("DELETE FROM user_learned_news WHERE user_id = ? AND news_id = ?", (uid, news_id))


async def remove_learned_video(uid: str, video_id: str):
    await execute("DELETE FROM user_learned_videos WHERE user_id = ? AND video_id = ?", (uid, video_id))


async def get_user_last_history(user_id: str) -> dict:
    query = "SELECT last_history FROM user WHERE uid = ?"
    result = await fetch_one(query, (user_id,))
    if result:
        return json.loads(result[0])
    return {}


async def get_all_uids() -> List[str]:
    query = "SELECT uid FROM user"
    results = await fetch_all(query)
    return [row[0] for row in results]


async def get_all_news() -> List[Tuple[str, str]]:
    query = "SELECT id, title FROM news"
    return await fetch_all(query)


async def get_all_videos() -> List[Tuple[str, str]]:
    query = "SELECT project_id, img_id FROM videos"
    return await fetch_all(query)


async def get_user_learned_news(uid: str) -> List[str]:
    query = "SELECT news_id FROM user_learned_news WHERE user_id = ?"
    results = await fetch_all(query, (uid,))
    return [row[0] for row in results]


async def get_user_learned_videos(uid: str) -> List[str]:
    query = "SELECT video_id FROM user_learned_videos WHERE user_id = ?"
    results = await fetch_all(query, (uid,))
    return [row[0] for row in results]


async def get_unlearned_content(user_id: str):
    # 获取所有news和videos内容
    all_news = await get_all_news()
    all_videos = await get_all_videos()

    # 获取用户已学习的news和videos
    learned_news_ids = await get_user_learned_news(user_id)
    learned_video_ids = await get_user_learned_videos(user_id)

    # 找出未学习的news和videos
    unlearned_news = [news for news in all_news if news[0] not in learned_news_ids]
    unlearned_videos = [video for video in all_videos if video[0] not in learned_video_ids]

    if not unlearned_news and not unlearned_videos:
        logger.warning(f"用户 {user_id} 已学习完所有内容!")

    return unlearned_news, unlearned_videos


async def update_user_learned_content(user_id: str, content_type: str, content_list: list):
    if content_type == 'news':
        # 获取用户已学习的news
        learned_news_ids = await get_user_learned_news(user_id)

        # 找出content_list中用户尚未学习的news
        unlearned_news_ids = [news_id for news_id in content_list if news_id not in learned_news_ids]

        # 添加这些news到用户的学习记录中
        for news_id in unlearned_news_ids:
            await add_learned_news(user_id, news_id)

    elif content_type == 'videos':
        # 获取用户已学习的videos
        learned_video_ids = await get_user_learned_videos(user_id)

        # 找出content_list中用户尚未学习的videos
        unlearned_video_ids = [video_id for video_id in content_list if video_id not in learned_video_ids]

        # 添加这些videos到用户的学习记录中
        for video_id in unlearned_video_ids:
            await add_learned_video(user_id, video_id)

    else:
        logger.error(f"未知的content_type: {content_type}")


async def update_user_headers(uid: str, headers: dict):
    """
    更新指定用户的headers。

    :param uid: 用户的ID
    :param headers: 新的headers数据
    """
    headers_str = json.dumps(headers)  # 将headers字典转换为字符串
    query = "UPDATE user SET headers = ? WHERE uid = ?"
    await execute(query, (headers_str, uid))
