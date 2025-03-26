from datetime import datetime
from sqlalchemy import or_, ForeignKey
from app.extensions import db
from app.models.tag import Tag
from app.models.category import Category

# Many-to-many relationship tables
prompt_categories = db.Table('prompt_categories',
    db.Column('prompt_id', db.Integer, ForeignKey('prompts.id'), primary_key=True),
    db.Column('category_id', db.Integer, ForeignKey('categories.id'), primary_key=True),
    db.Column('user_id', db.Integer, ForeignKey('users.id'), nullable=False, index=True)
)

prompt_tags = db.Table('prompt_tags',
    db.Column('prompt_id', db.Integer, ForeignKey('prompts.id'), primary_key=True),
    db.Column('tag_id', db.Integer, ForeignKey('tags.id'), primary_key=True),
    db.Column('user_id', db.Integer, ForeignKey('users.id'), nullable=False, index=True)
)

class Prompt(db.Model):
    __tablename__ = 'prompts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    categories = db.relationship(
        'Category',
        secondary=prompt_categories,
        lazy='subquery',
        primaryjoin="and_(Prompt.id==prompt_categories.c.prompt_id, "
                   "Prompt.user_id==prompt_categories.c.user_id)",
        backref=db.backref('prompts', lazy=True)
    )
    
    tags = db.relationship(
        'Tag',
        secondary=prompt_tags,
        lazy='subquery',
        primaryjoin="and_(Prompt.id==prompt_tags.c.prompt_id, "
                   "Prompt.user_id==prompt_tags.c.user_id)",
        backref=db.backref('prompts', lazy=True)
    )
    
    def __repr__(self):
        return f'<Prompt {self.title}>'
    
    # Virtual column for full-text search
    def to_dict(self):
        """返回提示信息字典"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'description': self.description,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'categories': [c.to_dict() for c in self.categories],
            'tags': [t.to_dict() for t in self.tags]
        }

    def search_content(self):
        """返回包含所有可搜索内容的字符串"""
        return f"{self.title} {self.content} {self.description or ''}"
    
    @classmethod
    def search(cls, query, user_id, page=1, per_page=10):
        """
        在用户范围内搜索提示。
        包括标签和类别的搜索。
        """
        # 基础搜索条件：必须属于当前用户
        base_condition = cls.user_id == user_id

        # 文本搜索
        text_search = (
            cls.title.contains(query) | 
            cls.content.contains(query) | 
            cls.description.contains(query)
        )
        
        # 标签名称搜索
        tag_search = cls.tags.any(Tag.name.contains(query))
        
        # 类别名称搜索
        category_search = cls.categories.any(Category.name.contains(query))
        
        # 组合所有搜索条件
        search_filter = base_condition & or_(text_search, tag_search, category_search)
        
        return cls.query.filter(search_filter).paginate(page=page, per_page=per_page)
