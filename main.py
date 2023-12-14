import asyncio
import base64
import json
import os
import webbrowser

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from loguru import logger
from quart import Quart, jsonify, request

import utils.database.db as db
from utils.config.config import Headers
from utils.database.db import init_db
from utils.get_item.get_items import get_points_or_token

AES_KEY = "abcdefghijklmnop"
AES_IV = "qrstuvwxzyabcdef"
DB_NAME = 'utils/database/main.db'
app = Quart(__name__, static_folder='./dist/build', static_url_path='/')


async def check_and_init_db(checked: bool = True):
    if checked:
        if not os.path.exists(DB_NAME):
            logger.warning(f"数据库不存在，正在初始化数据库...")
            await init_db()
            await check_and_init_db(checked=False)
        else:
            logger.info(f"数据库存在， 自动打开浏览器...")


async def format_data_for_frontend(news_data, last_history_data):
    formatted_data = []
    key_counter = 1

    for item in news_data:
        formatted_data.append({
            'key': str(key_counter),
            'type': 'news',
            'id': item['id'],
            'title': item['title'],
            'points': 2
        })
        key_counter += 1

    for item in last_history_data:
        formatted_data.append({
            'key': str(key_counter),
            'type': 'video',
            'id': item['project_id'],
            'title': item['img_id'],
            'points': 2
        })
        key_counter += 1

    return formatted_data


async def check(data: json) -> bool:
    logger.warning(f"check-1:{data.get('username')}")
    username = data.get('username')
    encrypted_password = data.get('password')
    decrypted_password = decrypt_aes(encrypted_password, AES_KEY, AES_IV)
    logger.error(f"解密的密码:{decrypted_password}")
    user = await db.fetch_one("SELECT password FROM user WHERE uid = ?", (username,))
    logger.warning(f"check-2:{user}")
    if not user:
        return False
    hashed_password = user[0]
    if not await db.check_password(hashed_password, decrypted_password):
        return False
    return True


def generate_headers(jsessionid, sessionid):
    headers_template = Headers.headers
    cookie_value = headers_template["Cookie"].format(jsessionid, sessionid)
    headers = {**headers_template, "Cookie": cookie_value}
    return headers


def decrypt_aes(encrypted_text, key, iv):
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
    decrypted_bytes = unpad(cipher.decrypt(base64.b64decode(encrypted_text)), AES.block_size)
    return decrypted_bytes.decode('utf-8')


@app.route('/')
async def index():
    return await app.send_static_file('index.html')


@app.route('/user/add', methods=['POST'])
async def register():
    logger.info(f"接收到登录请求")
    try:
        data = await request.json
    except Exception as e:
        logger.error(f"注册出现异常: {e}")
        return jsonify({"message": "注册失败"}), 500
    uid = data.get('username')
    password = data.get('password')
    # TODO 解密密码  用户 key v
    existing_user = await db.fetch_one("SELECT uid FROM user WHERE uid = ?", (uid,))
    if not existing_user:
        logger.info(f"接收到用户{uid}密码为{password}的注册请求")
        await db.insert_user(uid, password, headers=None, last_history=None)
    logger.info(f"接收到登录请求")
    return jsonify(True)


@app.route('/aes', methods=['GET'])
async def get_aes_key_and_iv():
    return jsonify({"key": AES_KEY, "iv": AES_IV})


@app.route('/list', methods=['POST'])
async def get_data_list():
    try:
        data = await request.json
    except Exception as e:
        logger.error(f"list获取出现异常: {e}")
        return jsonify({"message": "获取list失败"}), 500
    status = await check(data=data)
    if not status:
        return jsonify({"message": "验证失败"}), 400
    username = data.get('username')
    news_data = await db.get_user_learned_news(uid=username)
    last_history_data = await db.get_user_last_history(user_id=username)
    formatted_data = await format_data_for_frontend(news_data, [last_history_data])
    return jsonify(formatted_data)


@app.route('/user/point', methods=['POST'])
async def get_user_points():
    try:
        data = await request.json
    except Exception as e:
        logger.error(f"获取用户积分失败: {e}")
        return jsonify({"message": "获取失败"}), 500
    status = await check(data=data)
    if not status:
        return jsonify({"message": "验证失败"}), 400
    username = data.get('username')
    headers = await db.get_user_headers(user_id=username)
    total_points_value = await get_points_or_token(headers=headers, get_type='point')
    return jsonify({"points": total_points_value})


@app.route('/user/headers', methods=['POST'])
async def update_headers():
    try:
        data = await request.json
    except Exception as e:
        logger.error(f"更新请求头出现异常: {e}")
        return jsonify({"message": "更新失败"}), 500
    status = await check(data=data)
    logger.info(f"状态:{status}")
    if not status:
        return jsonify({"message": "验证失败"}), 400

    username = data.get('username')
    jsessionid = data.get('JSESSIONID')
    sessionid = data.get('sessionid')

    headers = generate_headers(jsessionid, sessionid)
    logger.info(f"生成的请求头:{headers}")
    await db.update_user_headers(uid=username, headers=headers)
    return jsonify({"message": "请求成功"}), 200


if __name__ == '__main__':
    asyncio.run(check_and_init_db())
    webbrowser.open_new('http://127.0.0.1:8009')
    app.run(host='0.0.0.0', port=8009)
