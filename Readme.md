python -m venv myenv

source myenv/bin/activate

pip install -r requirements.txt

python main.py

 & 'd:\code\spider_api_flask\myenv\Scripts\python.exe' 'c:\Users\1\.vscode\extensions\ms-python.debugpy-2025.4.1-win32-x64\bundled\libs\debugpy\launcher' '56123' '--' 'D:\code\spider_api_flask\scraper\other_scraper.py'

curl -X POST http://127.0.0.1:5000/fetch-app-details \
     -H "Content-Type: application/json" \
     -d '{"package_name": "389801252", "store": "ios"}'


{
  "app_name": "应用名称",
  "store": "应用商店",
  "package_name": "包名",
  "icon_url": "应用图标URL",
  "developer": "开发者",
  "version": "应用版本",
  "icp_number": "ICP备案号",
  "update_time": "版本更新时间"
}

{
  "app_name": "微信",
  "store": "ios",
  "package_name": "com.tencent.mm",
  "icon_url": "https://example.com/wechat_icon.png",
  "developer": "腾讯科技有限公司",
  "version": "8.0.1",
  "icp_number": "粤ICP备12018034号",
  "update_time": "2023-10-01T12:00:00Z"
}

