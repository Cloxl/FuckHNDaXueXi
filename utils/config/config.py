class URL:
    GET_NEWS_LIST_URL = "http://dxx.hngqt.org.cn/projecthn/list?time={time}"
    GET_VIDEOS_LIST_URL = "http://dxx.hngqt.org.cn/project/list?time={time}"
    GET_LEARNED_LIST_URL = "http://dxx.hngqt.org.cn/userPoint/list?time={time}"
    GET_POINT_URL = "http://dxx.hngqt.org.cn/project/index"
    LEARN_NEWS_URL = "http://dxx.hngqt.org.cn/historystudy/studyHnProjectAdd"
    LEARN_VIDEO_NEW_URL = "http://dxx.hngqt.org.cn/study/studyAdd20?time={time}"
    LEARN_VIDEO_HISTORY_URL = "http://dxx.hngqt.org.cn/historystudy/studyHistoryAdd?time={time}"
    GET_IMAGE_URL = "https://h5.cyol.com/special/daxuexi/{}/images/end.jpg"


class Key:
    pubkeySM2 = "301DF464D5C154D7EE79B07885048CB32ACF620E8C6A2F898A758F3F43E2AB62A44988559E2FAF5ACF84295D1E46B0615701AE74F064F28759ECAE1383787726"


class Time:
    Sleep_time = 1
    History_refresh = 7
    Day_refresh = "15:00"


class Headers:
    headers = {
        "Host": "dxx.hngqt.org.cn",
        "Connection": "keep-alive",
        "Content-Length": "404",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x6309080f) XWEB/8461 Flue",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "http://dxx.hngqt.org.cn",
        "Referer": "http://dxx.hngqt.org.cn/project/index",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cookie": "JSESSIONID={}; sessionid={}"
    }
