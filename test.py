import requests
import json

def get_interface_code():
    """
    从华为应用市场 API 获取动态的 interface-code
    :return: interface-code 或 None（失败时）
    """
    url = "https://web-drcn.hispace.dbankcloud.com/edge/webedge/getInterfaceCode"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "content-type": "application/json",
        "sec-ch-ua": "\"Microsoft Edge\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": "\"Android\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "Referer": "https://appgallery.huawei.com/",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }
    payload = {"params": {}, "zone": "", "locale": "zh"}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
        response.raise_for_status()
        # 假设返回的是纯文本
        interface_code = response.text.strip()
        return interface_code
    except requests.exceptions.RequestException as e:
        print(f"获取 interface-code 失败：{e}")
        return None

def fetch_huawei_app_details(app_id, user_locale="zh"):
    """
    通过华为应用市场 API 抓取应用详情
    :param app_id: 应用 ID（如 "C5683"）
    :param user_locale: 用户语言（默认 "zh"）
    :return: 响应数据或错误信息
    """
    # 获取 interface-code
    interface_code = get_interface_code()
    if not interface_code:
        return {"success": False, "error": "无法获取 interface-code"}

    # 发送请求获取应用详情
    url = "https://web-drcn.hispace.dbankcloud.com/edge/uowap/index"
    params = {
        "method": "internal.getTabDetail",
        "serviceType": "20",
        "reqPageNum": "1",
        "maxResults": "25",
        "uri": f"app|{app_id}",
        "shareTo": "",
        "currentUrl": f"https%3A%2F%2Fappgallery.huawei.com%2Fapp%2F{app_id}",
        "accessId": "",
        "appid": app_id,
        "zone": "",
        "locale": user_locale
    }
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "interface-code": interface_code,
        "sec-ch-ua": "\"Microsoft Edge\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "Referer": "https://appgallery.huawei.com/",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        print(response.json())
        return {"success": True, "data": response.json()}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}

# 示例调用
result = fetch_huawei_app_details("C5683")
if result["success"]:
    print("请求成功！", json.dumps(result["data"], indent=4, ensure_ascii=False))
else:
    print("请求失败！", result["error"])
