// diandian_intercept.js
function startIntercept() {
    const hookScript = document.createElement('script');
    hookScript.src = 'https://unpkg.com/ajax-hook@2.0.3/dist/ajaxhook.min.js';

    hookScript.onload = () => {
        window.__ajaxRequests = [];

        window._interceptor = ah.proxy({
            onRequest: (config, handler) => {
                handler.next(config);
            },
            // 在响应拦截部分替换为：
            onResponse: (response, handler) => {

                //处理URL匹配 https://api.diandian.com/pc/app/v2/word/search_related_contents
                if (response.config.url.includes('https://api.diandian.com/pc/app/v2/word/search_related_contents')) {
                                       
                    // 处理响应数据
                    json_response = JSON.parse(response.response);

                    if(json_response.code==0){
                        const responseRecord = {
                            type: 'search_related_contents',
                            url: response.config.url,
                            apps: json_response.data.app_list
                        };
    
                        console.log('responseRecord', responseRecord);
    
                            // 新增回调触发
                        if (window.__diandianCallback) {
                            window.__diandianCallback(responseRecord);
                        }
                        window.__ajaxRequests.push(responseRecord);
                    }
                    
                }
                
             
                handler.next(response);
            }
        });
    };

    hookScript.onerror = (error) => {
        console.error('[Diandian Hook] 脚本加载失败:', error);
        window.__hookStatus = 'error';
    };

    document.head.appendChild(hookScript);
    window.__hookStatus = 'pending';
}

// 暴露全局控制方法
// 修改全局控制方法
window.diandianHook = {
    start: startIntercept,
    getLogs: () => window.__ajaxRequests || [],
    clearLogs: () => (window.__ajaxRequests = []),
    stop: () => {
        _interceptor?.remove();
        window.__hookStatus = 'stopped';
    },
    // 替换为回调注册方法
    setCallback: (fn) => {
        window.__diandianCallback = fn;
    }
};

diandianHook.start();


