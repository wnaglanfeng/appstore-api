import requests

def fetch_xiaomi_app_details(package_name):
    """
    通过小米应用商店 API 抓取应用详情
    :param package_name: 应用包名
    :return: 应用详情
    """
    url = f"https://app.market.xiaomi.com/apm/app/package/{package_name}?os=1.1.1&model=unknown&ro=unknown&marketVersion=1914102&imei=cfcd208495d565ef66e7dff9f98764da&miuiBigVersionName=unknown&resolution=1080*1920&webResVersion=0&clientId=cfcd208495d565ef66e7dff9f98764da&densityScaleFactor=3&co=CN&pageConfigVersion=0&session=cfcd208495d565ef66e7dff9f98764da&deviceType=0&la=zh&sdk=19&mobileWeb=1&newUser=true&page=0&combine=1&h5=1&supportSlide=0&ref=&refs="
    
    try:
        response = requests.get(url, timeout=10)  # 设置超时时间
        response.raise_for_status()  # 检查请求是否成功
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}
    
    try:
        json_data = response.json()
        # 提取 app 相关字段
        app_data = json_data.get("app", {})

        # 构建标准返回对象
        standard_info = {
            "app_name": app_data.get("displayName", ""),  # 应用名称
            "store": "xiaomi",  # 应用商店
            "package_name": app_data.get("packageName", ""),  # 包名
            "icon_url": json_data.get("thumbnail","")+"webp/l168q80/"+ app_data.get("icon", ""),  # 应用图标
            "developer": app_data.get("publisherName", ""),  # 开发者
            "version": app_data.get("versionName", ""),  # 应用版本
            "icp_number": app_data.get("registrationNum", ""),  # ICP备案号
            "update_time": app_data.get("updateTime", ""),  # 版本更新时间
            "appTags": app_data.get("appTags", []),  # 应用标签
            "ratingTotalCount": app_data.get("ratingTotalCount", 0),  # 评分总数
            "rating": app_data.get("commentScore", 0),  # 应用评分
            "download_count": app_data.get("downloadCount", 0),  # 下载量
            "introduction": app_data.get("introduction", ""),  # 应用简介
            "screenshots": [json_data.get("thumbnail","")+"webp/rw240q80/"+ screenshot.strip() 
                           for screenshot in app_data.get("screenshot", "").split(',') 
                           if screenshot.strip()],  # 应用截图  # 应用截图
        }
        return {"success": True, "data": standard_info}

    except ValueError as e:
        return {"success": False, "error": "Invalid JSON response"}
    
    return {"success": False, "error": "App not found"}
