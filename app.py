from flask import Flask, request, jsonify
from scraper.ios_api import fetch_ios_app_details
from scraper.google_play_api import fetch_google_play_app_details
from scraper.xiaomi_api import fetch_xiaomi_app_details
from scraper.huawei_api import fetch_huawei_app_details
from scraper.other_scraper import fetch_other_app_details

app = Flask(__name__)

# 获取应用详情 - 同步接口
@app.route("/fetch-app-details", methods=["GET", "POST"])
def fetch_app_details_api():
    """
    API endpoint to fetch app details based on the provided app name, package name, and store type.
    """
    # 根据请求类型获取参数
    if request.method == "GET":
        app_name = request.args.get("app_name")
        package_name = request.args.get("package_name")
        store = request.args.get("store", "other")
    else:  # POST 方法
        data = request.json
        app_name = data.get("app_name")
        package_name = data.get("package_name")
        store = data.get("store", "other")

    # Check if neither app name nor package name is provided
    if not app_name and not package_name:
        # Return an error response if the input is invalid
        return jsonify({"error": "App name or package name is required"}), 400

    # Call different scraping methods based on the store type
    if store == "ios":
        # Fetch iOS app details using the package name
        result = fetch_ios_app_details(package_name)
    elif store == "google_play":
        # Fetch Google Play app details using the package name and API key
        result = fetch_google_play_app_details(package_name, api_key="YOUR_GOOGLE_API_KEY")
    elif store == "xiaomi":
        # Fetch Xiaomi app details using the package name
        result = fetch_xiaomi_app_details(package_name)
    elif store == "huawei":
        # Fetch Huawei app details using the package name and API key
        result = fetch_huawei_app_details(package_name, api_key="YOUR_HUAWEI_API_KEY")
    else:
        # Fetch details from other stores using the app name and package name
        result = fetch_other_app_details(app_name, package_name)

    # Return the result as a JSON response
    return jsonify(result)

# 首页
@app.route("/")
def home():
    return "Flask API Running!"

if __name__ == "__main__":
    app.run(debug=True)
