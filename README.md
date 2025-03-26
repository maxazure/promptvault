# PromptVault

PromptVault is a Flask and SQLite-based prompt management tool designed to help organize, search, and retrieve prompts efficiently.

## Features

- **User Authentication**: 
  - User registration and login system
  - Long-term session management (6 months)
  - Password reset functionality
  - Welcome emails for new users

- **Access Control**:
  - User-specific prompt management
  - Role-based access control (Admin/User)
  - Secure API access with JWT

- **Prompt Management**: 
  - Create, edit, delete, and organize prompts
  - Personal prompt collections for each user
  - Share prompts with specific users or groups

- **Categorization**: 
  - Assign categories and tags to prompts
  - User-specific categories and tags
  - Searchable dropdown selectors

- **Search Functionality**: 
  - Search prompts by title, content, tags, or categories
  - User-specific search results
  - Advanced filtering options

- **API Endpoints**: 
  - Access prompts programmatically via RESTful API
  - Secure authentication with JWT
  - Rate limiting and access control

- **Responsive UI**: 
  - User-friendly interface for both desktop and mobile
  - Enhanced user profile management
  - Intuitive navigation and controls

- **Enhanced Selection**: 
  - Interactive Select2 dropdowns for tags and categories
  - Search capability within dropdowns
  - Quick access to frequently used items

## Technology Stack

- **Backend**: 
  - Flask with SQLite (FTS5)
  - SQLAlchemy ORM
  - Flask-JWT-Extended for authentication
  - Flask-Mail for email services

- **Frontend**: 
  - HTML/Jinja2 templates
  - Bootstrap 5 UI framework
  - JavaScript/jQuery
  - Select2 for enhanced dropdowns

- **Authentication**:
  - JWT-based authentication
  - Bcrypt password hashing
  - Secure token management
  - Email verification system

- **API**: 
  - RESTful API architecture
  - JWT-protected endpoints
  - JSON response format
  - Comprehensive error handling

- **Development Tools**:
  - Flask-WTF for forms
  - Flask-Marshmallow for serialization
  - pytest for testing
  - Flask-Migrate for database migrations

## API Endpoints

1. **List Prompts** (with pagination)
   - `GET /api/prompts?page=1&per_page=10`
   - Optional filters: `category`, `tag`

2. **Search Prompts**
   - `GET /api/prompts/search?q=search_term&fields=title,content&page=1&per_page=10`

3. **Get Prompt Details**
   - `GET /api/prompts/<id>`

## Documentation

- [API Documentation](docs/api_auth.md) - 完整的API接口文档
- [部署指南](docs/deployment.md) - 部署和配置说明
- [TODO List](TODO.md) - 开发进度和功能清单

## Installation

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/promptvault.git
   cd promptvault
   ```

2. Create and activate a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (create a `.env` file)
   ```env
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   
   # JWT配置
   JWT_SECRET_KEY=your-jwt-secret-key
   JWT_ACCESS_TOKEN_EXPIRES=15552000
   
   # 邮件配置
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=true
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   ```

5. Initialize the database
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. Run the application
   ```bash
   flask run
   ```

## Usage

1. **Admin Interface**
   - Access the admin dashboard at `/admin`
   - Prompts Management:
     - Create, edit, and delete prompts
     - Assign categories and tags to prompts
   - Categories Management:
     - View all categories with descriptions
     - Create new categories with name and description
     - Edit existing categories
     - Delete categories (with usage check)
   - Tags Management:
     - View all tags in a clean list interface
     - Create new tags
     - Edit existing tags
     - Delete tags (with usage check)
   - Dashboard Overview:
     - Quick statistics for prompts, categories, and tags
     - Quick access buttons for common actions
   - Enhanced UI Features:
     - Searchable dropdown menus for categories and tags
     - Multi-select capabilities with keyboard support
     - Real-time search filtering of available options

2. **User Interface**
   - Search for prompts on the home page
   - View detailed information about each prompt
   - Copy prompts to clipboard with a single click

3. **API Usage**
   - Access prompts programmatically using the API endpoints
   - Integrate with other applications or scripts

## Development

1. Run tests
   ```
   pytest
   ```

2. Create a new migration after model changes
   ```
   flask db migrate -m "Description of changes"
   flask db upgrade
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
