import asyncio
import re
import json
import os
import pickle
from pyppeteer import launch
from pyppeteer.network_manager import Request, Response
from pyppeteer_stealth import stealth  # 防检测库

class DiandianInterceptor:
    def __init__(self, page):
        self.page = page
        self.intercepting = False
        self._callbacks = []
        self._pattern = re.compile(r'https://api\.diandian\.com/pc/app/v2/word/search_related_contents.*')

    def add_callback(self, func):
        self._callbacks.append(func)

    async def _setup_network_listener(self):
        """配置网络请求监听"""
        async def on_response(res: Response):
            if self._pattern.search(res.url):
                try:
                    data = await res.json()
                    intercepted = {
                        'url': res.url,
                        'status': res.status,
                        'method': res.request.method,
                        'data': data
                    }
                    for cb in self._callbacks:
                        cb(intercepted)
                except Exception as e:
                    print(f'响应解析失败: {str(e)}')

        self.page.on('response', lambda res: asyncio.ensure_future(on_response(res)))

    async def start(self):
        """启动拦截监听"""
        await self._inject_runtime()
        # self.page.on('console', self._handle_console)
        await self._setup_network_listener()  # 新增网络监听
        self.intercepting = True

    async def stop(self):
        self.intercepting = False

    async def _inject_runtime(self):
        """注入监控脚本"""
        # current_dir = os.path.dirname(os.path.abspath(__file__))
        # js_path = os.path.join(current_dir, 'diandian_intercept.js')
        # with open(js_path, 'r', encoding='utf-8') as f:
        #     intercept_js = f.read()
        """注入监控脚本"""
         
        # 确保脚本在新页面加载时也生效
         

    def _handle_console(self, msg):
        """处理控制台日志"""
        print(f"[控制台日志] {msg.text}")
        if '[DIANDIAN_DATA]' in msg.text:
            try:
                json_str = re.search(r'\[DIANDIAN_DATA\](.*)', msg.text).group(1)
                data = json.loads(json_str)
                for cb in self._callbacks:
                    cb(data)
            except Exception as e:
                print(f'Console处理错误: {str(e)}')

async def fetch_other_app_details(app_name=None, package_name=None):
    # 配置浏览器路径（按实际情况修改）★WIN示例路径★
    chrome_path = r'C:\Users\1\AppData\Local\pyppeteer\pyppeteer\local-chromium\1181205\chromedriver-win64\chrome-win\chrome.exe'
   
    # 浏览器配置
    browser = await launch(
        headless=False,               # 有界面模式
       args=[
            "--start-maximized",       # 最大化窗口
            "--disable-infobars",
            "--no-sandbox",
            "--disable-web-security",  # 禁用同源策略
            "--disable-features=IsolateOrigins,site-per-process",  # 禁用站点隔离
        ],
        defaultViewport=None,          # 禁用默认视口设置
        executablePath=chrome_path,
        userDataDir='./user_data',  # 持久化用户数据
    )
    
    page = await browser.newPage()
    await stealth(page)  # 反检测
    
    # 启动拦截器
    interceptor = DiandianInterceptor(page)
    
    def callback(data):
        if 'search_related_contents' in data['url']:
            print(f"\n=== 捕获到关键词相关数据 ==="
            f"\n请求方法: {data['method']}"
            f"\n响应数据样本: {data['data']}")
        else:
            # 其他请求的通用处理
            print(f"[拦截数据] {data['url']} -> Status: {data['status']}")

    interceptor.add_callback(callback)
    await interceptor.start()

    # 尝试恢复登录态
    cookie_file = 'auth_state.pkl'
    if os.path.exists(cookie_file):
        with open(cookie_file, 'rb') as f:
            cookies = pickle.load(f)
            await page.setCookie(*cookies)

    await page.goto('https://www.diandian.com', {'waitUntil': 'networkidle2'})
    
    # 检查登录状态
    if not await is_logged_in(page):
        print("需要重新登录...")
        await perform_login(page)
        # 保存新的Cookies
        cookies = await page.cookies()
        with open(cookie_file, 'wb') as f:
            pickle.dump(cookies, f)

    # 导航到搜索页面
    # await page.goto('https://app.diandian.com', {'waitUntil': 'networkidle2'})

    # 获取应用数据
    
    search_key = app_name or package_name
    try:

        #选择应用平台
        platforms = {
            'Google Play': '.dd-google-logo-16',
            'App Store': '.dd-apple-logo-16',
            '国内安卓': '.dd-android-logo-16',
            'TapTap': '.dd-taptap-logo-16'
        }
        platform_selector = '.iconfont.Dianxiala1'  # 根据实际页面调整选择器
        await page.waitForSelector(platform_selector)
        await page.click(platform_selector)

        # 选择平台
        selected_platform = 'Google Play'  # 可根据需要动态选择
        await page.click(platforms[selected_platform])

        #下拉输入，选择地区
        location_selector = '.country-logo'
        await page.waitForSelector(location_selector)
        await page.click(location_selector)

        # 选择地区
        selected_location = '澳大利亚'  # 可根据需要动态选择
        #根据text选择
         # 使用 XPath 选择器
        location_elements = await page.xpath(f'//div//span[contains(text(), "{selected_location}")]')
        if location_elements:
            await location_elements[0].click()
        else:
            raise Exception(f"未找到地区: {selected_location}")

        # 使用组合属性定位器
        input_xpath = '//input[contains(@class, "el-input__inner") and (@placeholder="搜索应用名称/包名" or @placeholder="搜索应用名称/App ID")]'
        try:
            # 等待输入框可见且可交互（增加等待时间）
            input_element = await page.waitForXPath(
                input_xpath,
                {
                    'visible': True,
                    'timeout': 15000,  # 延长到15秒
                    'polling': 500      # 每500ms检查一次
                }
            )

            # 先清空原内容（针对可能存在的默认值）
            await input_element.click(clickCount=3)  # 全选
            await page.keyboard.press('Backspace')

            await input_element.type(search_key, {'delay': 100})  # 逐字输入，模拟人工输入

            # 验证输入内容（可选调试步骤）
            current_value = await page.evaluate('input => input.value', input_element)
            print(f'当前输入值: {current_value}')

            # 触发搜索建议（部分页面需要这一步才会显示下拉）
            await page.keyboard.press('ArrowDown')
            await asyncio.sleep(0.5)

        except Exception as e:
            print(f'输入失败: {str(e)}')
            await page.screenshot({'path': 'input_error.png'})
        # # 输入搜索关键词
        # input_selector = 'input.search-input'
        # await page.waitForSelector(input_selector, timeout=5000)
        # await page.type(input_selector, search_key)
        
        # # 点击搜索
        # await page.keyboard.press('Enter')
        # await page.waitForNavigation({'waitUntil': 'networkidle2'})

        
        
        # 等待API数据捕获
        await asyncio.sleep(3)

        # 挂机等待
        while True:
            await asyncio.sleep(10)


        return {'status': 'success'}
        
    except Exception as e:
        print(f'主流程异常: {str(e)}')
        return {'error': str(e)}
    finally:
        await interceptor.stop()
        await browser.close()

async def is_logged_in(page) -> bool:
    """检查登录状态"""
    try:
        user_info = await page.evaluate('''() => {
            const info = localStorage.getItem('userInfo');
            try { return info ? JSON.parse(info) : null } catch { return null }
        }''')
        
        # 判断本地存储的认证信息
        if user_info and user_info.get('uid'):
            print(f"本地用户存在: {user_info['uid']}")
            return True

        # 检查有效Cookies
        cookies = await page.cookies()
        valid_cookies = [c for c in cookies if c['name'] in ('m_token', 'token')]
        return len(valid_cookies) > 0
        
    except Exception as e:
        print(f'登录状态检查失败: {str(e)}')
        return False

async def perform_login(page):
    """执行登录流程"""
    await page.goto('https://www.diandian.com/login', {'waitUntil': 'networkidle2'})
    
    # 切换邮箱登录
    email_btn = await page.waitForSelector('.login-type-switch .email-btn', timeout=5000)
    await email_btn.click()
    
    # 输入凭据
    await page.type('#email-input', '254437106@qq.com')
    await page.type('#password-input', 'Abc@12345')
    
    # 提交表单
    submit_btn = await page.waitForSelector('button.login-submit')
    await submit_btn.click()
    
    # 等待登录完成
    await page.waitForNavigation({'waitUntil': 'networkidle2'})
    await page.waitFor(2000)  # 确保完成登录后操作

if __name__ == '__main__':
    result = asyncio.get_event_loop().run_until_complete(
        fetch_other_app_details(app_name="AI")
    )
    print('最终结果:', result)
