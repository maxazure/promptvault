# PromptVault 项目结构

```
promptvault/
├── .clinerules            # 项目规则配置文件
├── .clineignore           # 忽略文件配置
├── .env                   # 环境变量文件
├── .env.example           # 环境变量示例文件
├── .gitignore             # Git忽略文件配置
├── Dockerfile             # Docker构建文件
├── docker-compose.yml     # Docker Compose配置
├── config.py              # 应用配置
├── README.md              # 项目说明
├── requirements.txt       # Python依赖
├── run.py                 # 应用入口
├── app/                   # 主应用目录
│   ├── __init__.py        # 应用初始化
│   ├── extensions.py      # Flask扩展
│   ├── models/            # 数据模型
│   │   ├── __init__.py
│   │   ├── category.py
│   │   ├── prompt.py
│   │   ├── tag.py
│   │   └── user.py
│   ├── routes/            # 路由控制器
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── api.py
│   │   ├── auth.py
│   │   └── main.py
│   ├── static/            # 静态资源
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── images/
│   │   │   └── avatar.svg
│   │   └── js/
│   │       ├── admin.js
│   │       ├── auth-check.js
│   │       └── main.js
│   ├── templates/         # 模板文件
│   │   ├── base.html
│   │   ├── admin/         # 管理后台模板
│   │   │   ├── categories.html
│   │   │   ├── category_form.html
│   │   │   ├── index.html
│   │   │   ├── prompt_form.html
│   │   │   ├── prompts.html
│   │   │   ├── tag_form.html
│   │   │   ├── tags.html
│   │   │   └── users.html
│   │   ├── auth/          # 认证相关模板
│   │   │   ├── change_password.html
│   │   │   ├── forgot_password.html
│   │   │   ├── login.html
│   │   │   ├── profile.html
│   │   │   ├── register.html
│   │   │   └── reset_password.html
│   │   └── main/          # 主页面模板
│   │       ├── index.html
│   │       └── prompt_detail.html
│   └── utils/             # 工具类
│       ├── __init__.py
│       ├── auth_decorators.py
│       └── search.py
├── instance/              # 实例文件夹
│   └── promptvault.db     # 数据库配置文件(已迁移到MySQL)
└── migrations/            # 数据库迁移
    ├── alembic.ini
    ├── env.py
    ├── README
    ├── script.py.mako
    └── versions/
        └── 8fa90a7eef81_initial_database_setup_with_user_.py
├── .github/               # GitHub配置
    └── workflows/         # GitHub Actions工作流
        └── docker-build-push.yml  # Docker构建和推送工作流
```

## 主要功能模块

1. **核心应用** (app/)
   - 模型: 用户、提示词、分类、标签
   - 路由: 认证、管理、API、主路由
   - 静态资源: CSS、JS、图片
   - 模板: 基于Flask的Jinja2模板

2. **数据库管理**
   - SQLAlchemy ORM模型
   - Alembic数据库迁移

3. **配置管理**
   - 环境变量(.env)
   - 应用配置(config.py)
