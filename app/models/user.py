from datetime import datetime, timedelta
import bcrypt
import secrets
from app.extensions import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(80))
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Password reset fields
    reset_token = db.Column(db.String(100), unique=True)
    reset_token_expires = db.Column(db.DateTime)

    # Relationships
    categories = db.relationship('Category', backref='user', lazy=True)
    tags = db.relationship('Tag', backref='user', lazy=True)
    prompts = db.relationship('Prompt', backref='user', lazy=True)

    def __init__(self, email, password, name=None):
        self.email = email.lower()
        self.set_password(password)
        self.name = name
        # 检查是否是第一个用户，如果是则设为管理员
        if not User.query.first():
            self.is_admin = True

    def set_password(self, password):
        """设置密码哈希"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password):
        """验证密码"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def generate_reset_token(self):
        """生成密码重置令牌"""
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expires = datetime.utcnow() + timedelta(hours=24)
        db.session.commit()
        return self.reset_token

    def verify_reset_token(self, token):
        """验证重置令牌"""
        if (self.reset_token != token or 
            not self.reset_token_expires or 
            self.reset_token_expires < datetime.utcnow()):
            return False
        return True

    def reset_password(self, token, new_password):
        """重置密码"""
        if not self.verify_reset_token(token):
            return False
        self.set_password(new_password)
        self.reset_token = None
        self.reset_token_expires = None
        db.session.commit()
        return True

    def to_dict(self):
        """返回用户信息字典"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<User {self.email}>'
