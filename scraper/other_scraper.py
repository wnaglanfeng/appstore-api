from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
# 持久化登录状态示例
import pickle

def fetch_other_app_details(app_name=None, package_name=None):
    """
    通过 Selenium 抓取其他应用商店的应用详情
    :param app_name: 应用名称
    :param package_name: 应用包名
    :return: 应用详情
    """
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # 无头模式
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    # 在浏览器选项中添加
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option(
        "excludeSwitches", ["enable-automation"]
    )
    options.add_experimental_option(
        "useAutomationExtension", False
    )

    driver = webdriver.Chrome(options=options)
    # 显式窗口最大化（优先级高于参数）🌟
    driver.maximize_window()

    try:
       
        driver.get("https://www.diandian.com/")
        # 等待页面加载完成
        time.sleep(5)  # 等待页面加载
        # 恢复登录
        with open("auth_state.pkl", "rb") as f:
            for cookie in pickle.load(f):
                driver.add_cookie(cookie)
        driver.refresh()  # 刷新后生效

        # 等待页面加载完成
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # 查找并点击登录按钮
        login_button = driver.find_element(By.CSS_SELECTOR, '.dd-login-btn .dd-pointer')
        login_button.click()

        # 等待登录弹框加载
        # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.login-modal .email-login')))

        # 选择邮箱登录
        # 查找并点击“邮箱登录”按钮
        email_login_button = driver.find_element(By.CSS_SELECTOR, '.footer-item:nth-child(2) .footer-btn')
        email_login_button.click()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.email-login')))

        print("已切换到邮箱登录界面")
         # 等待邮箱输入框加载完成
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.email-login input[type="text"]'))
        )
        email_input.send_keys("254437106@qq.com")  # 替换为您的邮箱

        # 等待密码输入框加载完成
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.email-login input[type="password"]'))
        )
        password_input.send_keys("Abc@12345")  # 替换为您的密码

        # 点击登录按钮
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button.login-btn')
            )
        )
        submit_button.click()

        # 保存Cookie
        import pickle
        with open("auth_state.pkl", "wb") as f:
            pickle.dump(driver.get_cookies(), f)

        # 等待登录完成（可根据实际情况调整时间）
        time.sleep(5)
        print("登录成功")

       

        # return {"success": True, "name": name, "description": description}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        driver.quit()


fetch_other_app_details(app_name="微信")