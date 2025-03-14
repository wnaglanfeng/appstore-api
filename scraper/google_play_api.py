import requests

def fetch_google_play_app_details(package_name, api_key):
    """
    通过 Google Play API 抓取应用详情
    :param package_name: 应用包名
    :param api_key: Google Play API 密钥
    :return: 应用详情
    """
    url = f"https://www.googleapis.com/androidpublisher/v3/applications/{package_name}/details"
    params = {"key": api_key}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return {
            "success": True,
            "name": data.get("title"),
            "description": data.get("description"),
        }
    return {"success": False, "error": "App not found"}
