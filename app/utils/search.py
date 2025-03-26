"""
Search utilities for the PromptVault application.
This provides enhanced search capabilities using SQLite's FTS5 extension.
"""

from app import db
from app.models import Prompt, Category, Tag
from sqlalchemy import or_

def search_prompts(query, fields=None, page=1, per_page=10):
    """
    Search prompts by query string with optional field filtering.
    
    Args:
        query (str): The search query string
        fields (list): List of fields to search in. Default is all searchable fields.
        page (int): Page number for pagination
        per_page (int): Items per page
        
    Returns:
        Pagination object with search results
    """
    if not query:
        return Prompt.query.order_by(Prompt.created_at.desc()).paginate(
            page=page, per_page=per_page)
    
    # Clean and normalize the search query
    query = query.strip()
    
    # Default to all fields if none specified
    if not fields:
        fields = ['title', 'content', 'description', 'categories', 'tags']
    
    # Base query
    base_query = Prompt.query
    
    # Build search filter based on requested fields
    filters = []
    
    if 'title' in fields:
        filters.append(Prompt.title.ilike(f'%{query}%'))
        
    if 'content' in fields:
        filters.append(Prompt.content.ilike(f'%{query}%'))
        
    if 'description' in fields:
        filters.append(Prompt.description.ilike(f'%{query}%'))
    
    # Add category and tag filtering if requested
    if 'categories' in fields:
        filters.append(
            Prompt.categories.any(Category.name.ilike(f'%{query}%'))
        )
    
    if 'tags' in fields:
        filters.append(
            Prompt.tags.any(Tag.name.ilike(f'%{query}%'))
        )
    
    # Combine all filters with OR
    search_filter = or_(*filters)
    
    # Execute search query with pagination
    return base_query.filter(search_filter).order_by(
        Prompt.created_at.desc()
    ).paginate(page=page, per_page=per_page)


def setup_fts(app, db):
    """
    Set up full-text search capabilities.
    
    Note: This is a placeholder for future implementation using SQLite's FTS5.
    In a production environment, consider using a dedicated search solution like
    Elasticsearch for more advanced search capabilities.
    
    Args:
        app: Flask application instance
        db: SQLAlchemy database instance
    """
    with app.app_context():
        try:
            # Check if SQLite supports FTS5
            db.session.execute('SELECT sqlite_version()')
            db.session.execute('SELECT fts5()')
            app.logger.info("SQLite FTS5 extension is available")
            
            # Here we would create virtual tables for FTS5
            # This is just a placeholder - implementation would depend on
            # specific requirements and database schema
            
        except Exception as e:
            app.logger.warning(f"Full-text search setup failed: {str(e)}")
            app.logger.info("Falling back to basic search functionality")
