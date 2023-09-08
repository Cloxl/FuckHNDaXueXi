import base64

from crypto.Random import get_random_bytes
from quart import Quart, request, jsonify

app = Quart(__name__, static_folder='./dist', static_url_path='/')

users = {}


@app.route('/')
async def index():
    return await app.send_static_file('index.html')


@app.route('/status/check', methods=['GET'])
async def check_status():
    return jsonify(status=True)


@app.route('/adduser/check', methods=['POST'])
async def check_user():
    data = await request.json
    user_id = data.get('user_id')
    if user_id in users:
        return jsonify(check=False)
    else:
        return jsonify(check=True)


@app.route('/adduser', methods=['POST'])
async def add_user():
    data = await request.json
    user_id = data.get('user_id')
    password = data.get('password')
    headers = data.get('headers')
    print(f"user_id: {user_id}\tpwd: {password}\thead: {headers}")
    if user_id not in users:
        users[user_id] = {
            'password': password,
            'headers': headers
        }
        return jsonify(status=True)
    else:
        return jsonify(status=False)


@app.route('/adduser/aes', methods=['GET'])
async def get_aes_credentials():
    key = get_random_bytes(16)
    iv = get_random_bytes(16)
    return jsonify({
        'key': base64.b64encode(key).decode('utf-8'),
        'iv': base64.b64encode(iv).decode('utf-8')
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=11220)
