from flask import Blueprint, render_template, request, current_app
from app.models import Prompt, Category, Tag

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
def index():
    """Main page and search interface."""
    # Get categories and tags for filters
    categories = Category.query.all()
    tags = Tag.query.all()
    
    # Handle search query and filters
    query = request.args.get('query', '')
    tag_id = request.args.get('tag', type=int)
    category_id = request.args.get('category', type=int)
    page = request.args.get('page', 1, type=int)
    
    # Start with base query
    prompts_query = Prompt.query

    if tag_id:
        # Filter by tag if tag_id is provided
        prompts_query = prompts_query.join(Prompt.tags).filter(Tag.id == tag_id)
    
    if category_id:
        # Filter by category if category_id is provided
        prompts_query = prompts_query.join(Prompt.categories).filter(Category.id == category_id)
    
    if query:
        # If search query provided, perform search within the filtered results
        search_filter = (
            Prompt.title.contains(query) |
            Prompt.content.contains(query) |
            Prompt.description.contains(query)
        )
        prompts_query = prompts_query.filter(search_filter)
    
    # Apply ordering and pagination
    prompts = prompts_query.order_by(Prompt.created_at.desc()).paginate(
        page=page, per_page=current_app.config['PROMPTS_PER_PAGE'])
    
    return render_template('main/index.html', 
                          prompts=prompts, 
                          categories=categories, 
                          tags=tags,
                          query=query)

@main.route('/prompts/<int:id>')
def prompt_detail(id):
    """Display details for a specific prompt."""
    prompt = Prompt.query.get_or_404(id)
    return render_template('main/prompt_detail.html', prompt=prompt)
