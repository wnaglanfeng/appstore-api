import requests

def fetch_ios_app_details(package_name):
    """
    通过苹果商店 API 抓取应用详情
    :param package_name: 应用包名
    :return: 应用详情
    """
    url = f"https://itunes.apple.com/lookup?id={package_name}&country=cn"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        #TODO 返回结果格式如下：
        # {
        #     "data": {
        #         "appTags": [
        #             {
        #                 "link": "sametag/434",
        #                 "tagId": 434,
        #                 "tagName": "交友"
        #             },
        #             {
        #                 "link": "sametag/426",
        #                 "tagId": 426,
        #                 "tagName": "聊天社交"
        #             }
        #         ],
        #         "app_name": "微信",
        #         "developer": "广州腾讯科技有限公司",
        #         "download_count": 10172691538,
        #         "icon_url": "https://sf0.market.xiaomi.com/thumbnail/webp/l168q80/AppStore/069c660eaecea4fa8ba4eb72a384cff1c813c2602",
        #         "icp_number": "粤B2-20090059-1621A（备案公司：深圳市腾讯计算机系统有限公司）",
        #         "introduction": "你可以通过音视频通话、群聊、朋友圈来和朋友们分享生活，可以通过公众号、视频号获得文章、视频内容，以及通过小程序方便地使用生活服务，还可以开启「关怀模式」，文字与按钮更大更清晰。",
        #         "package_name": "com.tencent.mm",
        #         "rating": 3.9,
        #         "ratingTotalCount": 34856,
        #         "screenshots": [
        #             "https://sf0.market.xiaomi.com/thumbnail/webp/rw240q80/AppStore/0d36372fe3973487eb03b27c0968a197f27763388",
        #             "https://sf0.market.xiaomi.com/thumbnail/webp/rw240q80/AppStore/07e2b28eb0fb545f19591700dac04c6fbea9c9d96",
        #             "https://sf0.market.xiaomi.com/thumbnail/webp/rw240q80/AppStore/0bd211fdc93c44fed8b082c82c4391340329fddd2",
        #             "https://sf0.market.xiaomi.com/thumbnail/webp/rw240q80/AppStore/03064c2e1527b4cab8046d71371ae09fefab67767",
        #             "https://sf0.market.xiaomi.com/thumbnail/webp/rw240q80/AppStore/0c1ca47c85e124c999c218fa758a94e7d57f44fdf"
        #         ],
        #         "store": "xiaomi",
        #         "update_time": 1741089971495,
        #         "version": "8.0.56"
        #     },
        #     "success": true
        # }
        print(data)
        if data["resultCount"] > 0:
            app_info = data["results"][0]

            app_tags = []
            genre_ids=app_info.get("genreIds", [])
            genres=app_info.get("genres", [])   
                         
            for tag_id, tag_name in zip(genre_ids, genres):
                # 构建 tagId 为整数类型
                tag_id_int = int(tag_id)
                # 构建每个标签的字典
                tag_dict = {
                    # "link": f"sametag/{tag_id_int}",
                    "tagId": tag_id_int,
                    "tagName": tag_name
                }
                app_tags.append(tag_dict)
                
            return {
                "success": True,
                "data":  {
                    "app_name": app_info.get("trackName", ""),  # 应用名称
                    "app_id": package_name,  # 包名或 App ID
                    "bundleId":app_info.get("bundleId"),  # 包名或 App ID
                    "developer": app_info.get("sellerName", ""),  # 开发者
                    "icon_url": app_info.get("artworkUrl512", app_info.get("artworkUrl100", "")),  # 图标 URL
                    "rating": app_info.get("averageUserRating", 0.0),  # 评分
                    "ratingTotalCount": app_info.get("userRatingCount", 0),  # 评分人数
                    "introduction": app_info.get("description", ""),  # 应用介绍
                    "screenshots": app_info.get("screenshotUrls", []),  # 截图 URL 列表
                    "version": app_info.get("version", ""),  # 版本号
                    "update_time": app_info.get("currentVersionReleaseDate", ""),  # 更新时间
                    "store": "apple",  # 商店名称
                    "download_count": 0,  # 苹果商店不提供下载量
                    "icp_number": "",  # 苹果商店不提供 ICP 备案号
                    "appTags":app_tags,  # 苹果商店不提供标签信息
                    "download_url": app_info.get("trackViewUrl", "")  # 下载链接
            }
            }
    return {"success": False, "error": "App not found"}
