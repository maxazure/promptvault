from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, url_for, render_template, make_response
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity,
    get_current_user, set_access_cookies,
    set_refresh_cookies
)
from flask_mail import Message
from app.extensions import db, jwt, mail
from app.models.user import User

auth = Blueprint('auth', __name__)


def send_reset_email(user):
    """发送密码重置邮件"""
    token = user.generate_reset_token()
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    msg = Message('重置您的密码',
                 recipients=[user.email])
    msg.body = f'''您好，

您请求重置密码。请点击以下链接重置密码：

{reset_url}

如果您没有请求重置密码，请忽略此邮件。

此链接将在24小时后过期。
'''
    mail.send(msg)

def send_welcome_email(user):
    """发送欢迎邮件"""
    msg = Message('欢迎加入 PromptVault',
                 recipients=[user.email])
    msg.body = f'''您好 {user.name or user.email}，

欢迎加入 PromptVault！

我们很高兴您的加入。现在您可以：
- 创建和管理您的提示词
- 使用标签和分类组织提示词
- 搜索和发现有用的提示词

如果您有任何问题，请随时联系我们。

祝您使用愉快！
'''
    mail.send(msg)

@auth.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    if not data:
        return jsonify({'message': '无效的请求数据'}), 400

    # 验证必要字段
    for field in ['email', 'password']:
        if not data.get(field):
            return jsonify({'message': f'缺少必要字段: {field}'}), 400

    # 验证邮箱格式
    import re
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    if not email_pattern.match(data['email']):
        return jsonify({'message': '无效的邮箱格式'}), 400

    # 验证密码强度
    if len(data['password']) < 8:
        return jsonify({'message': '密码长度必须至少为8个字符'}), 400

    # 检查邮箱是否已注册
    if User.query.filter_by(email=data['email'].lower()).first():
        return jsonify({'message': '该邮箱已注册'}), 409

    # 创建新用户
    try:
        user = User(
            email=data['email'],
            password=data['password'],
            name=data.get('name')
        )
        
        db.session.add(user)
        db.session.commit()

        # 发送欢迎邮件
        try:
            send_welcome_email(user)
        except Exception as e:
            current_app.logger.error(f'发送欢迎邮件失败: {str(e)}')

        # 生成Token
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return jsonify({
            'message': '注册成功',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'用户注册失败: {str(e)}')
        return jsonify({'message': '注册失败，请稍后重试'}), 500

@auth.route('/register', methods=['GET'])
def register_page():
    """注册页面"""
    return render_template('auth/register.html')

@auth.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    if not data:
        return jsonify({'message': '无效的请求数据'}), 400

    # 验证必要字段
    for field in ['email', 'password']:
        if not data.get(field):
            return jsonify({'message': f'缺少必要字段: {field}'}), 400

    user = User.query.filter_by(email=data['email'].lower()).first()
    if user and user.check_password(data['password']):
        if not user.is_active:
            return jsonify({'message': '账号已被禁用'}), 403

        # 使用更长的过期时间
        access_token = create_access_token(identity=str(user.id), fresh=True)
        refresh_token = create_refresh_token(identity=str(user.id))

        # 创建响应并设置cookie
        response = jsonify({
            'message': '登录成功',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        })
        
        # 设置token到cookie中，并禁用CSRF保护
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        
        # 添加跨域头
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        
        return response
    
    return jsonify({'message': '邮箱或密码错误'}), 401

@auth.route('/login', methods=['GET'])
def login_page():
    """登录页面"""
    return render_template('auth/login.html')

@auth.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新访问令牌"""
    identity = get_jwt_identity()
    access_token = create_access_token(identity=str(identity))
    
    # 创建响应并设置cookie
    response = jsonify({
        'access_token': access_token,
        'message': 'Token刷新成功'
    })
    
    # 设置新的访问token到cookie中
    set_access_cookies(response, access_token)
    
    return response

@auth.route('/forgot-password', methods=['POST'])
def forgot_password():
    """请求重置密码"""
    data = request.get_json()
    if not data or not data.get('email'):
        return jsonify({'message': '请提供邮箱地址'}), 400

    user = User.query.filter_by(email=data['email'].lower()).first()
    if user:
        try:
            send_reset_email(user)
            return jsonify({'message': '重置密码邮件已发送'})
        except Exception as e:
            current_app.logger.error(f'发送重置密码邮件失败: {str(e)}')
            return jsonify({'message': '发送重置密码邮件失败'}), 500
    
    return jsonify({'message': '如果邮箱存在，重置密码邮件将发送至该邮箱'}), 200

@auth.route('/forgot-password', methods=['GET'])
def forgot_password_page():
    """忘记密码页面"""
    return render_template('auth/forgot_password.html')

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """重置密码"""
    if request.method == 'GET':
        # 返回重置密码页面
        return render_template('auth/reset_password.html', token=token)

    data = request.get_json()
    if not data or not data.get('password'):
        return jsonify({'message': '请提供新密码'}), 400

    if not data.get('email'):
        return jsonify({'message': '请提供邮箱地址'}), 400

    user = User.query.filter_by(email=data['email'].lower()).first()
    if not user:
        return jsonify({'message': '用户不存在'}), 404

    if user.reset_password(token, data['password']):
        return jsonify({'message': '密码重置成功'})
    
    return jsonify({'message': '重置链接无效或已过期'}), 400


@auth.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """更新用户信息"""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    data = request.get_json()
    if not data:
        return jsonify({'message': '无效的请求数据'}), 400

    if 'name' in data:
        user.name = data['name']

    if 'password' in data:
        user.set_password(data['password'])

    user.updated_at = datetime.now(datetime.timezone.utc)  # 使用UTC时间，确保时区一致性
    db.session.commit()

    return jsonify({
        'message': '个人信息更新成功',
        'user': user.to_dict()
    })

@auth.route('/profile/data', methods=['GET'])
@jwt_required()
def get_profile_data():
    """返回用户信息的 JSON 数据"""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    return jsonify({
        'name': user.name,
        'email': user.email,
        'created_at': user.created_at.isoformat()
    })


@auth.route('/profile', methods=['GET'])
def profile_page():
    """个人资料页面"""
    return render_template('auth/profile.html')

@auth.route('/change-password', methods=['GET'])
def change_password_page():
    """修改密码页面"""
    return render_template('auth/change_password.html')

@auth.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改密码"""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    data = request.get_json()
    if not data:
        return jsonify({'message': '无效的请求数据'}), 400
    
    # 验证必要字段
    for field in ['current_password', 'new_password']:
        if not data.get(field):
            return jsonify({'message': f'缺少必要字段: {field}'}), 400
    
    # 验证当前密码
    if not user.check_password(data['current_password']):
        return jsonify({'message': '当前密码错误'}), 401
    
    # 验证新密码强度
    if len(data['new_password']) < 8:
        return jsonify({'message': '新密码长度必须至少为8个字符'}), 400
    
    # 更新密码
    user.set_password(data['new_password'])
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': '密码修改成功'})

@auth.route('/logout', methods=['POST'])
@jwt_required(optional=True)
def logout():
    """用户注销"""
    from flask_jwt_extended import unset_jwt_cookies
    
    response = jsonify({'message': '成功退出登录'})
    unset_jwt_cookies(response)
    return response

# JWT错误处理
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    current_app.logger.error(f"Expired token, header: {jwt_header}, payload: {jwt_payload}")
    return jsonify({
        'message': 'Token已过期',
        'error': 'token_expired'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    current_app.logger.error(f"Invalid token: {error}")
    return jsonify({
        'message': '无效的Token',
        'error': 'invalid_token'
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    current_app.logger.error(f"Missing token error: {error}")
    return jsonify({
        'message': '缺少Token',
        'error': 'authorization_required'
    }), 401

# 修改JWT配置函数
def configure_jwt_for_app(app):
    """配置JWT相关参数"""
    app.config['JWT_COOKIE_SECURE'] = app.config.get('JWT_COOKIE_SECURE', False)
    # 修改：仅从cookies中查找token，避免header中存在错误token影响验证
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400  # 24小时
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 2592000  # 30天
    app.config['JWT_COOKIE_SAMESITE'] = 'Lax'

# 在Blueprint注册时配置JWT
@auth.record_once
def on_load(state):
    app = state.app
    configure_jwt_for_app(app)

# 添加CORS相关处理
@auth.after_request
def add_cors_headers(response):
    """添加跨域响应头"""
    response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@auth.route('/options', methods=['OPTIONS'])
def options():
    """处理预检请求"""
    response = jsonify({'message': 'OK'})
    response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@auth.route('/verify-token', methods=['GET'])
@jwt_required()
def verify_token():
    """验证当前token"""
    user_id = get_jwt_identity()
    return jsonify({
        'message': 'Token有效',
        'user_id': user_id
    })
