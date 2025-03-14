import re
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import pickle
import os
import json
import base64
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities




class RequestInterceptor:

    def __init__(self, driver):
        self.driver = driver
        self.callbacks = []
        self.is_monitoring = False
    
    def add_callback(self, func):
        self.callbacks.append(func)
    
    def start_monitoring(self, interval=0.5):
        def log_poller():
            while self.is_monitoring:
                print("日志轮询中...")
                try:
                    logs = self.driver.get_log('browser')
                    print(f"日志数量: {len(logs)}")
                    self.process_logs(logs)
                except Exception as e:
                    print(f"日志轮询异常: {str(e)}")
                time.sleep(interval)
        
        self.is_monitoring = True
        threading.Thread(target=log_poller, daemon=True).start()
    
    def stop_monitoring(self):
        self.is_monitoring = False
    
    def extract_json_from_log(self, log_line):
        # 匹配 [DIANDIAN_DATA] 后的JSON内容（支持多行）
        json_match = re.search(r'\[DIANDIAN_DATA\]\s*(\{.*?\})(?=\s*$|\s*\")', log_line, re.DOTALL)
        
        if json_match:
            try:
                # 直接解析标准JSON
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                # 修复常见格式错误
                fixed_json = json_match.group(1)
                # 1. 处理末尾逗号
                fixed_json = re.sub(r',\s*}(?=\s*$)', '}', fixed_json)
                # 2. 处理转义字符
                fixed_json = fixed_json.replace("\\", '')
                # 3. 转换单引号为双引号
                fixed_json = fixed_json.replace("'", '"')
                return json.loads(fixed_json)
        
        # 防御性二次提取
        parts = log_line.split("[DIANDIAN_DATA]")
        if len(parts) > 1:
            # 处理控制台转义字符（如\"）
            json_str = parts[1].strip(' "').encode().decode('unicode_escape')
            return json.loads(json_str)
        
        raise ValueError("未找到有效JSON数据")

    def process_logs(self, logs):
        for entry in logs:
            # print(f"日志内容: {entry['message']}")
        
            if '[DIANDIAN_DATA]' in entry['message']:
                  
                try:
                  
                    data = self.extract_json_from_log(entry['message'])
                    for callback in self.callbacks:
                        callback(data)
                except Exception as e:
                    print(f"日志解析失败: {str(e)}")


def inject_intercept(driver, timeout=10):
    try:
        # 等待页面基本加载完成
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        js_path = os.path.join(current_dir, 'diandian_intercept.js')
        
        with open(js_path, 'r', encoding='utf-8') as f:
            js_code = f.read()
        
        driver.execute_script(f"""
            {js_code}
            diandianHook.setCallback(function(data) {{
                console.log('[DIANDIAN_DATA]' + JSON.stringify(data));
            }});
            diandianHook.start();
        """)
    except FileNotFoundError:
        print(f"❌ 未找到脚本文件: {js_path}")
    except Exception as e:
        print(f"💥 注入失败: {str(e)}")


def fetch_other_app_details(app_name=None, package_name=None):
    capabilities = DesiredCapabilities.CHROME
    capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}
    
   # 修改浏览器初始化配置
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--disable-web-security')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    # 新增日志级别设置
    options.set_capability('goog:loggingPrefs', {'browser': 'ALL', 'performance': 'ALL'})

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    try:
        driver.get("https://www.diandian.com/robots.txt")
        time.sleep(2)

        cookie_file = "auth_state.pkl"
        if os.path.exists(cookie_file):
            print("\033[32m检测到Cookie文件，尝试恢复登录状态\033[0m")
            try:
                with open(cookie_file, "rb") as f:
                    cookies = pickle.load(f)
                    driver.delete_all_cookies()
                    for cookie in cookies:
                        if "diandian.com" in cookie["domain"]:
                            driver.add_cookie(cookie)
                print(f"已加载{len(cookies)}个有效Cookie")
                driver.refresh()
            except Exception as e:
                print(f"Cookie加载失败: {str(e)}")

        search_key = app_name or package_name
        target_url = f"https://www.diandian.com"
        driver.get(target_url)

        if not is_logged_in(driver):
            print("\033[33m需要重新登录\033[0m")
            perform_login(driver)
        else:
            print("\033[32m已通过Cookie保持登录状态\033[0m")

        print("\033[36m注入拦截器...\033[0m")
        try:
            interceptor = RequestInterceptor(driver)
            
            def handle_request(data):
                print(f"拦截到请求: {data['url']}")
                if data['type'] == 'response':
                    print(f"响应状态码: {data['status']}")
            
            driver.get("https://www.diandian.com")
            interceptor.add_callback(handle_request)
            time.sleep(2)
            inject_intercept(driver)
            interceptor.start_monitoring()
            print("\033[36m开始抓取应用详情...\033[0m")
            while True:
                # 卡住主线程，等待日志回调
                time.sleep(10)

            
        finally:
            interceptor.stop_monitoring()
            driver.quit()

        print("\033[36m开始抓取应用详情...\033[0m")
        return scrape_data(driver)

    except Exception as e:
        print(f"\033[31m发生未捕获的异常: {str(e)}\033[0m")
        return {"success": False, "error": str(e)}
    finally:
        driver.quit()
        print("\033[35m浏览器实例已安全关闭\033[0m")


def is_logged_in(driver: webdriver.Chrome) -> bool:
    try:
        user_info = driver.execute_script(
            "return JSON.parse(localStorage.getItem('userInfo')) || {};"
        )
        
        required_fields = ['uid', 'email', 'phone']
        if all(user_info.get(field) for field in required_fields):
            print(f"本地用户信息验证通过 UID: {user_info['uid']}")
            return True

        auth_cookies = ['m_token', 'token']
        current_time = int(time.time())
        
        valid_cookies = [
            c for c in driver.get_cookies()
            if c['name'] in auth_cookies and 
               ('expiry' not in c or c['expiry'] > current_time)
        ]
        
        if len(valid_cookies) >= 1:
            print(f"发现有效认证Cookie: {[c['name'] for c in valid_cookies]}")
            return True

        try:
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".user-avatar"))
            )
            return True
        except TimeoutException:
            try:
                return not driver.find_element(By.CSS_SELECTOR, "button.login-btn").is_displayed()
            except:
                return False

    except Exception as e:
        print(f"登录状态检测异常: {str(e)}")
        return False

    return False


def perform_login(driver):
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    login_button = driver.find_element(By.CSS_SELECTOR, '.dd-login-btn .dd-pointer')
    login_button.click()

    email_login_button = driver.find_element(By.CSS_SELECTOR, '.footer-item:nth-child(2) .footer-btn')
    email_login_button.click()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.email-login')))

    print("已切换到邮箱登录界面")
    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.email-login input[type="text"]'))
    )
    email_input.send_keys("254437106@qq.com")

    password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.email-login input[type="password"]'))
    )
    password_input.send_keys("Abc@12345")

    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'button.login-btn')
        )
    )
    submit_button.click()

    with open("auth_state.pkl", "wb") as f:
        pickle.dump(driver.get_cookies(), f)
    print("已更新登录状态缓存")


def scrape_data(driver):
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".app-detail-card"))
        )
        
        return {
           
        }
    except Exception as e:
        print(f"数据抓取失败: {str(e)}")
        return {"error": str(e)}

result = fetch_other_app_details(app_name="微信")
print("抓取结果：", result)
