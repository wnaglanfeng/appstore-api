import requests

def fetch_huawei_app_details(package_name, api_key):
    """
    通过华为应用商店 API 抓取应用详情
    :param package_name: 应用包名
    :param api_key: 华为应用商店 API 密钥
    :return: 应用详情
    """
    
    # 请求 URL
    url = "https://web-drcn.hispace.dbankcloud.com/edge/single/filtered"

    # 请求头
    headers = {
        "accept": "application/json, text/plain, */*"
    }

    # 请求体
    data = {
        "pkgName": "com.tencent.mm",
        "zone": "",
        "locale": "zh"
    }

    # 发送 POST 请求
    response = requests.post(url, headers=headers, json=data)

    print(response)
   
    # 检查响应状态码
    if response.status_code == 200:
        print("请求成功！")
        print("响应数据：", response.json())
        # 提取应用信息
        app_info = response.json().get("appInfo", {})
        # 构建标准返回对象
        standard_info = {
            "appTags": [],  # 应用标签（华为 API 未提供，需补充）
            "app_name": app_info.get("name", ""),  # 应用名称
            "developer": app_info.get("devName", ""),  # 开发者
            "download_count": int(app_info.get("downCount", "0")),  # 下载量
            "icon_url": app_info.get("icon", ""),  # 应用图标
            "icp_number": "",  # ICP 备案号（华为 API 未提供，需补充）
            "introduction": app_info.get("intro", ""),  # 应用简介
            "package_name": app_info.get("pkgName", ""),  # 包名
            "rating": 0.0,  # 评分（华为 API 未提供，需补充）
            "ratingTotalCount": 0,  # 评分人数（华为 API 未提供，需补充）
            "screenshots": app_info.get("screenImgs", []),  # 截图列表
            "store": "huawei",  # 应用商店
            "update_time": 0,  # 更新时间（华为 API 未提供，需补充）
            "version": app_info.get("version", ""),  # 版本号
            "download_url": app_info.get("url", "")  # 下载链接
        }
        return {"success": True, "data": standard_info}


    else:
        print(f"请求失败，状态码：{response.status_code}")
        print("错误信息：", response.text)
    return {"success": False, "error": "App not found"}
