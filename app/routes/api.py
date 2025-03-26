from flask import Blueprint, jsonify, request, current_app
from app.models import Prompt, Category, Tag
from app.extensions import db, ma

api = Blueprint('api', __name__)

# Schema for serializing prompts
class TagSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name')

class CategorySchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description')

class PromptSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'content', 'description', 'created_at', 'updated_at', 'categories', 'tags')
    
    categories = ma.Nested(CategorySchema, many=True)
    tags = ma.Nested(TagSchema, many=True)

prompt_schema = PromptSchema()
prompts_schema = PromptSchema(many=True)

@api.route('/prompts', methods=['GET'])
def get_prompts():
    """
    Get a paginated list of prompts with optional filtering by category or tag.
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', current_app.config['PROMPTS_PER_PAGE'], type=int)
    
    # Base query
    query = Prompt.query
    
    # Apply filters if provided
    category_id = request.args.get('category', type=int)
    tag_id = request.args.get('tag', type=int)
    
    if category_id:
        query = query.join(Prompt.categories).filter(Category.id == category_id)
    
    if tag_id:
        query = query.join(Prompt.tags).filter(Tag.id == tag_id)
    
    # Execute query with pagination
    paginated_prompts = query.order_by(Prompt.created_at.desc()).paginate(
        page=page, per_page=per_page)
    
    # Prepare response
    result = {
        'prompts': prompts_schema.dump(paginated_prompts.items),
        'pagination': {
            'page': paginated_prompts.page,
            'per_page': paginated_prompts.per_page,
            'total_pages': paginated_prompts.pages,
            'total_items': paginated_prompts.total
        }
    }
    
    return jsonify(result)

@api.route('/prompts/search', methods=['GET'])
def search_prompts():
    """
    Search prompts by query string with optional field filtering.
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', current_app.config['PROMPTS_PER_PAGE'], type=int)
    query = request.args.get('q', '')
    fields = request.args.get('fields', 'all')
    
    if not query:
        return jsonify({
            'prompts': [],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_pages': 0,
                'total_items': 0
            }
        })
    
    # This is a placeholder. In a real implementation, we would use SQLite FTS5
    # and filter by specific fields based on the 'fields' parameter
    paginated_prompts = Prompt.search(query, page, per_page)
    
    result = {
        'prompts': prompts_schema.dump(paginated_prompts.items),
        'pagination': {
            'page': paginated_prompts.page,
            'per_page': paginated_prompts.per_page,
            'total_pages': paginated_prompts.pages,
            'total_items': paginated_prompts.total
        }
    }
    
    return jsonify(result)

@api.route('/prompts/<int:id>', methods=['GET'])
def get_prompt(id):
    """
    Get details for a specific prompt.
    """
    prompt = Prompt.query.get_or_404(id)
    return jsonify(prompt_schema.dump(prompt))
