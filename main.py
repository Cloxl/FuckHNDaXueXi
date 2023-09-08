import base64
import json

from crypto.Cipher import AES
from crypto.Util.Padding import unpad
from quart import Quart, jsonify, request

import utils.database.db as db
from utils.get_item.get_points import get_points

app = Quart(__name__)

# Use a fixed AES key and iv
AES_KEY = "abcdefghijklmnop"
AES_IV = "qrstuvwxzyabcdef"


async def decode_and_format_headers(encoded_request_header: bytes) -> dict:
    # Base64解码
    decoded_request_header = base64.b64decode(encoded_request_header).decode('utf-8')

    # 将HTTP请求头转换为字典
    headers_list = decoded_request_header.split('\n')
    headers_dict = {}
    for header in headers_list:
        if ': ' in header:
            key, value = header.split(': ', 1)
            headers_dict[key] = value

    return headers_dict


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
    username = data.get('username')
    encrypted_password = data.get('password')
    decrypted_password = decrypt_aes(encrypted_password, AES_KEY, AES_IV)
    user = await db.fetch_one("SELECT password FROM user WHERE uid = ?", (username,))
    if not user:
        return False
    hashed_password = user[0]
    if not await db.check_password(hashed_password, decrypted_password):
        return False
    return True


@app.route('/user/add', methods=['POST'])
async def register():
    data = await request.json
    uid = data.get('uid')
    password = data.get('password')
    existing_user = await db.fetch_one("SELECT uid FROM user WHERE uid = ?", (uid,))
    if not existing_user:
        await db.insert_user(uid, password, headers=None, last_history=None)
    return jsonify(True)


@app.route('/aes', methods=['GET'])
async def get_aes_key_and_iv():
    return jsonify({"key": AES_KEY, "iv": AES_IV})


@app.route('/list', methods=['POST'])
async def get_data_list():
    data = await request.json
    status = await check(data=data)
    if not status:
        return
    username = data.get('username')
    news_data = await db.get_user_learned_news(uid=username)
    last_history_data = await db.get_user_last_history(user_id=username)
    formatted_data = await format_data_for_frontend(news_data, [last_history_data])
    return jsonify(formatted_data)


@app.route('/user/point', methods=['POST'])
async def get_user_points():
    data = await request.json
    status = await check(data=data)
    if not status:
        return
    username = data.get('username')
    headers = await db.get_user_headers(user_id=username)
    total_points_value = await get_points(headers=headers)
    return jsonify({"points": total_points_value})


@app.route('/user/headers', methods=['POST'])
async def update_headers():
    data = await request.json
    status = await check(data=data)
    if not status:
        return
    username = data.get('username')
    headers_base64 = base64.b64decode(data.get('requestHeader'))
    headers = await decode_and_format_headers(encoded_request_header=headers_base64)
    await db.update_user_headers(uid=username, headers=headers)
    return jsonify({"message": "请求成功"}), 200


def decrypt_aes(encrypted_text, key, iv):
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
    decrypted_bytes = unpad(cipher.decrypt(base64.b64decode(encrypted_text)), AES.block_size)
    return decrypted_bytes.decode('utf-8')


if __name__ == '__main__':
    app.run()
