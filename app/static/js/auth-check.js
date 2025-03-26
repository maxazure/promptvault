/**
 * auth-check.js - 处理用户认证状态检查和相关UI交互
 * 
 * 功能：
 * 1. 页面加载时检查用户登录状态
 * 2. 根据登录状态显示/隐藏相应的导航元素
 * 3. 处理用户登出操作
 * 4. 管理认证相关的cookie和本地存储
 */

// 在DOM加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化认证状态检查
    checkAuthStatus();
    
    // 绑定登出按钮事件
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
    
    // 初始化登录表单提交事件（如果在登录页面）
    initLoginForm();
    
    // 初始化注册表单提交事件（如果在注册页面）
    initRegisterForm();
});

/**
 * 检查用户认证状态并更新UI
 */
function checkAuthStatus() {
    // 从localStorage获取用户信息
    const userInfo = getUserFromStorage();
    
    // 获取导航元素
    const authNav = document.querySelectorAll('.auth-nav');
    const unauthNav = document.querySelectorAll('.unauth-nav');
    const adminNav = document.querySelectorAll('.admin-nav');
    const adminMenuItem = document.querySelectorAll('.admin-menu-item');
    
    if (userInfo) {
        // 用户已登录，显示认证后的导航元素
        authNav.forEach(el => el.style.display = 'block');
        unauthNav.forEach(el => el.style.display = 'none');
        
        // 更新用户信息显示
        const userEmail = document.getElementById('userEmail');
        if (userEmail) {
            userEmail.textContent = userInfo.name || userInfo.email;
        }
        
        // 如果用户是管理员，显示管理员导航和菜单项
        if (userInfo.is_admin) {
            adminNav.forEach(el => el.style.display = 'block');
            adminMenuItem.forEach(el => el.style.display = 'block');
        } else {
            adminNav.forEach(el => el.style.display = 'none');
            adminMenuItem.forEach(el => el.style.display = 'none');
        }
        
        // 检查token是否即将过期，如果是则刷新
        checkAndRefreshToken();
    } else {
        // 用户未登录，显示未认证的导航元素
        authNav.forEach(el => el.style.display = 'none');
        unauthNav.forEach(el => el.style.display = 'block');
        adminNav.forEach(el => el.style.display = 'none');
        adminMenuItem.forEach(el => el.style.display = 'none');
    }
}

/**
 * 从localStorage获取用户信息
 * @returns {Object|null} 用户信息对象或null
 */
function getUserFromStorage() {
    const userJson = localStorage.getItem('user');
    if (userJson) {
        try {
            return JSON.parse(userJson);
        } catch (e) {
            console.error('解析用户信息失败:', e);
            return null;
        }
    }
    return null;
}

/**
 * 处理用户登出
 */
function handleLogout() {
    // 发送登出请求到服务器
    fetch('/auth/logout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin' // 包含cookies
    })
    .then(response => {
        if (response.ok) {
            // 清除本地存储的用户信息和token
            localStorage.removeItem('user');
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            
            // 重定向到首页
            window.location.href = '/';
        } else {
            throw new Error('登出失败');
        }
    })
    .catch(error => {
        console.error('登出错误:', error);
        showAlert('登出失败，请稍后重试', 'danger');
    });
}

/**
 * 检查token是否即将过期，如果是则刷新
 */
function checkAndRefreshToken() {
    const token = localStorage.getItem('access_token');
    if (!token) return;
    
    // 解析JWT token（不验证签名）
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));

        const payload = JSON.parse(jsonPayload);
        const expiryTime = payload.exp * 1000; // 转换为毫秒
        const currentTime = Date.now();
        const timeToExpiry = expiryTime - currentTime;
        
        // 如果token将在15分钟内过期，刷新它
        if (timeToExpiry < 15 * 60 * 1000 && timeToExpiry > 0) {
            refreshToken();
        }
    } catch (e) {
        console.error('解析token失败:', e);
    }
}

/**
 * 刷新访问token
 */
function refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) return;
    
    fetch('/auth/refresh', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${refreshToken}`
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.access_token) {
            localStorage.setItem('access_token', data.access_token);
        }
    })
    .catch(error => {
        console.error('刷新token失败:', error);
    });
}

/**
 * 初始化登录表单提交事件
 */
function initLoginForm() {
    const loginForm = document.getElementById('loginForm');
    if (!loginForm) return;
    
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // 表单验证
        if (!loginForm.checkValidity()) {
            e.stopPropagation();
            loginForm.classList.add('was-validated');
            return;
        }
        
        // 获取表单数据
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        // 发送登录请求
        fetch('/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (data.message === '登录成功') {
                // 保存用户信息和token到本地存储
                localStorage.setItem('user', JSON.stringify(data.user));
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('refresh_token', data.refresh_token);
                
                // 重定向到首页
                window.location.href = '/';
            } else {
                throw new Error(data.message || '登录失败');
            }
        })
        .catch(error => {
            console.error('登录错误:', error);
            showAlert(error.message || '登录失败，请检查邮箱和密码', 'danger');
        });
    });
}

/**
 * 初始化注册表单提交事件
 */
function initRegisterForm() {
    const registerForm = document.getElementById('registerForm');
    if (!registerForm) return;
    
    registerForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // 表单验证
        if (!registerForm.checkValidity()) {
            e.stopPropagation();
            registerForm.classList.add('was-validated');
            return;
        }
        
        // 获取表单数据
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const name = document.getElementById('name')?.value || '';
        
        // 发送注册请求
        fetch('/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password, name }),
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (data.message === '注册成功') {
                // 保存用户信息和token到本地存储
                localStorage.setItem('user', JSON.stringify(data.user));
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('refresh_token', data.refresh_token);
                
                // 显示成功消息并重定向
                showAlert('注册成功！正在跳转...', 'success');
                setTimeout(() => {
                    window.location.href = '/';
                }, 1500);
            } else {
                throw new Error(data.message || '注册失败');
            }
        })
        .catch(error => {
            console.error('注册错误:', error);
            showAlert(error.message || '注册失败，请稍后重试', 'danger');
        });
    });
}

console.log('auth-check.js loaded and initialized');