from functools import wraps
from flask import jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from app.models.user import User
import json
import jwt

def require_permission(permission):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                # 验证请求中的JWT令牌，通常位于HTTP请求头的Authorization字段
                # 格式为："Bearer <token>"
                verify_jwt_in_request()
                
                # 调试信息：获取并打印JWT令牌内容
                jwt_token = get_jwt()
                user_id = get_jwt_identity()
                
                # 确保user_id是字符串类型
                if user_id is not None and not isinstance(user_id, str):
                    user_id = str(user_id)
                    
                current_user = User.query.get(user_id) if user_id else None
                
                if not current_user:
                    return jsonify(msg='用户不存在或已失效'), 401
                
                if not current_user.has_permission(permission):
                    return jsonify(msg='权限不足'), 403
                    
                return fn(*args, **kwargs)
            except jwt.exceptions.InvalidSubjectError:
                current_app.logger.error("JWT错误: Subject必须是字符串类型")
                return jsonify(msg='认证失败，令牌格式错误'), 401
            except Exception as e:
                import traceback
                error_detail = {
                    'error': str(e),
                    'type': type(e).__name__,
                    'traceback': traceback.format_exc()
                }
                current_app.logger.error(f"JWT认证错误: {str(e)}")
                return jsonify(msg='认证失败，请重新登录', error=error_detail), 401
        return decorator
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        try:
            # 验证请求中的JWT令牌，通常位于HTTP请求头的Authorization字段
            # 格式为："Bearer <token>"
            verify_jwt_in_request()
            
            user_id = get_jwt_identity()
            current_app.logger.error(f"user_id: {user_id}")
            # 确保user_id是字符串类型
            if user_id is not None and not isinstance(user_id, str):
                user_id = str(user_id)
                
            current_user = User.query.get(user_id) if user_id else None
            
            if not current_user:
                return jsonify(msg='用户不存在'), 401
            if not current_user.is_active:
                return jsonify(msg='账户已被禁用'), 403
            if not current_user.is_admin:
                return jsonify(msg='需要管理员权限'), 403
            # 将当前用户信息传递给被装饰的函数
            kwargs['current_user'] = current_user
            return fn(*args, **kwargs)
        except jwt.exceptions.InvalidSubjectError:
            current_app.logger.error("JWT错误: Subject必须是字符串类型1")
            return jsonify(msg='认证失败，令牌格式错误'), 401
        except Exception as e:
            import traceback
            error_detail = {
                'error': str(e),
                'type': type(e).__name__,
                'traceback': traceback.format_exc()
            }
            current_app.logger.error(f"JWT认证错误1: {str(e)}")
            return jsonify(
                msg='认证失败，请重新登录',
                error=error_detail
            ), 401
    return decorator

def get_current_user():
    user_id = get_jwt_identity()
    if isinstance(user_id, str) and user_id.isdigit():
        user_id = int(user_id)
    
    return User.query.get(user_id)
