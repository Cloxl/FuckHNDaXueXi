const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const requestHeader = document.getElementById('request-header');
const submitBtn = document.getElementById('submit-btn');
const checkIcon = document.getElementById('check-icon');
const BASE_URL = 'http://127.0.0.1:11220';

let aesKey = null;
let aesIV = null;
let lastInputTime = null;
let usernameChecked = false;

fetch(`${BASE_URL}/adduser/aes`).then(response => response.json()).then(data => {
    aesKey = data.key;
    aesIV = data.iv;
}).catch(error => {
    console.error("Error fetching AES credentials:", error);
});


usernameInput.addEventListener('input', (e) => {
    if (!usernameInput.value.trim()) {
        checkIcon.style.display = 'none';  // 如果框为空，隐藏图标
        return;
    }
    clearTimeout(lastInputTime);
    lastInputTime = setTimeout(() => {
        fetch(`${BASE_URL}/adduser/check`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: usernameInput.value
            })
        }).then(response => response.json()).then(data => {
            if (data.check) {
                checkIcon.src = '/imgs/succeed.png';
                checkIcon.classList.add('success');
                checkIcon.classList.remove('error');
                usernameChecked = true;
                checkIcon.style.display = 'block';  // 显示图标
            } else {
                checkIcon.src = '/imgs/error.png';
                checkIcon.classList.add('error');
                checkIcon.classList.remove('success');
                usernameChecked = false;
                checkIcon.style.display = 'block';  // 显示图标
            }
            checkIcon.style.display = 'block';
            checkIcon.style.display = 'block';
        }).catch(error => {
            console.error("Error:", error);
        });
    }, 2000);
});

requestHeader.addEventListener('input', (e) => {
    const value = e.target.value;
    const lines = value.split('\n').length;
    const maxHeight = Math.min(lines, 20) * 20;

    // 添加动画效果
    requestHeader.style.transition = 'height 0.9s ease';
    e.target.style.height = `${maxHeight}px`;
});

// 提交数据
submitBtn.addEventListener('click', async () => {
    if (!usernameChecked) {
        alert('你需要先更改用户名');
        return;
    }
    if (!usernameInput.value || !passwordInput.value || !requestHeader.value) {
        alert('请填写所有必要的内容');
        return;
    }

    const encodedHeaders = btoa(requestHeader.value);

    try {
        const passwordEncrypted = await encryptWithAES(passwordInput.value, aesKey, aesIV); // 使用AES加密

        const response = await fetch(`${BASE_URL}/adduser`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: usernameInput.value,
                password: passwordEncrypted,
                headers: encodedHeaders
            })
        });

        const data = await response.json();
        if (data.status) {
            alert('添加成功');
        } else {
            alert('添加失败，可能发生了某些错误');
        }
    } catch (error) {
        console.error("Error:", error);
        alert('后端连接超时或其他错误');
    }
});


const timeout = (ms, promise) => {
    return new Promise((resolve, reject) => {
        const timer = setTimeout(() => {
            reject(new Error("timeout"));
        }, ms);
        promise.then(response => {
            clearTimeout(timer);
            resolve(response);
        }, reject);
    });
}

timeout(5000, fetch(`${BASE_URL}/status/check`)).then(response => response.json()).then(data => {
    if (data.status) {
        alert('后端连接成功');
    } else {
        alert('后端连接失败');
    }
}).catch(error => {
    if (error.message === "timeout") {
        alert('后端连接超时');
    } else {
        console.error("Error:", error);
    }
});

async function encryptWithAES(text, key, iv) {
    // 将key和iv从base64转换为ArrayBuffer
    const keyBuffer = Uint8Array.from(atob(key), c => c.charCodeAt(0));
    const ivBuffer = Uint8Array.from(atob(iv), c => c.charCodeAt(0));

    // 使用Web Crypto API进行加密
    const encoder = new TextEncoder();
    const data = encoder.encode(text);
    const cryptoKey = await window.crypto.subtle.importKey(
        'raw',
        keyBuffer,
        {name: 'AES-CBC', length: 128},
        false,
        ['encrypt', 'decrypt']
    );
    const encryptedData = await window.crypto.subtle.encrypt(
        {name: 'AES-CBC', iv: ivBuffer},
        cryptoKey,
        data
    );

    // 将ArrayBuffer转换为base64，以便于传输
    const encryptedArray = new Uint8Array(encryptedData);
    return btoa(String.fromCharCode(...encryptedArray));
}
