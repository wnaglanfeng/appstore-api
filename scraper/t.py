from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import json
import time
import base64

class CDPNetworkInterceptor:
    def __init__(self):
        self.captured_responses = []
        self.init_driver()
        self.enable_network_monitor()

    def init_driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        self.driver = webdriver.Chrome(options=chrome_options)

    def enable_network_monitor(self):
        """Step1: 启用网络域监控"""
        self.driver.execute_cdp_cmd('Network.enable', {})
        
    def parse_perf_logs(self):
        """Step2: 解析性能日志捕获响应"""
        start_time = time.time()
        max_wait = 10000  # 最长等待时间
        
        while time.time() - start_time < max_wait:
            # 核心捕获逻辑
            logs = self.driver.get_log('performance')
            for log in logs:
                try:
                    msg = json.loads(log['message'])['message']
                    method = msg.get('method')
                    
                    # 筛选响应接收事件
                    if method == 'Network.responseReceived':
                        params = msg['params']
                        res_url = params['response'].get('url', '')
                        print(f"捕获到响应：{res_url}")
                         
                            
                except (json.JSONDecodeError, KeyError) as e:
                    continue
            time.sleep(0.5)  # 降低CPU消耗
        
        raise TimeoutError("未能捕获到目标响应")

    def process_response(self, params):
        """Step3: 处理抓取的响应内容"""
        request_id = params['requestId']
        
        # 获取完整响应体
        response_body = self.driver.execute_cdp_cmd(
            'Network.getResponseBody',
            {'requestId': request_id}
        )
        
        # 构建结果结构
        self.captured_responses.append({
            'url': params['response']['url'],
            'status': params['response']['status'],
            'headers': params['response']['headers'],
            'body': self.decode_body(response_body)
        })

    def decode_body(self, res_body):
        """自动解码 body 内容"""
        if res_body.get('base64Encoded', False):
            return base64.b64decode(res_body['body']).decode('utf-8', errors='ignore')
        return res_body.get('body', '')

    def search_demo(self, keyword):
        """Demo执行流程：搜索并抓包"""
        
        
        # 导航到目标页面
        self.driver.get(f"https://app.diandian.com")
        
        # 主动触发数据请求（根据实际情况调整）
      
        # 捕获指定API的响应
        self.parse_perf_logs()
        return self.captured_responses[-1]

# 使用示例
interceptor = CDPNetworkInterceptor()
result = interceptor.search_demo("微信")
print(json.dumps(result, indent=2, ensure_ascii=False))
