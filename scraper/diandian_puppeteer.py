import asyncio
from pyppeteer import launch
from pyppeteer.chromium_downloader import chromium_executable

# 下载 Chromium
# download_chromium()


async def main():
    # 配置浏览器路径（按实际情况修改）★WIN示例路径★
    chrome_path = r'C:\Users\1\AppData\Local\pyppeteer\pyppeteer\local-chromium\1181205\chromedriver-win64\chrome-win\chrome.exe'
    # 启动浏览器
    browser = await launch(headless=False, args=['--no-sandbox', '--disable-setuid-sandbox'], executablePath=chrome_path)
    page = await browser.newPage()

    # 注册回调函数
    await page.exposeFunction('onDataReceived', lambda data: print('收到回调数据:', data))

    # 导航到目标页面
    await page.goto('https://www.diandian.com/robots.txt')

    # 注入 JavaScript 代码
    await page.evaluate('''() => {
        // 模拟一些操作
        const data = {
            title: document.title,
            timestamp: Date.now()
        };

        // 调用注册的回调函数
        window.onDataReceived(data);
    }''')

    # 关闭浏览器
    await browser.close()

# 运行异步任务
asyncio.get_event_loop().run_until_complete(main())