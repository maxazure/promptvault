# Import models to make them available when importing from app.models
from app.models.prompt import Prompt, prompt_categories, prompt_tags
from app.models.category import Category
from app.models.tag import Tag
from app.models.user import User