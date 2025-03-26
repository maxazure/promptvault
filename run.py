import os
from dotenv import load_dotenv
from app import create_app
from app.extensions import db
from app.models import Prompt, Category, Tag, prompt_categories, prompt_tags

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

app = create_app(os.getenv('FLASK_ENV') or 'default')

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Prompt': Prompt,
        'Category': Category,
        'Tag': Tag,
        'prompt_categories': prompt_categories,
        'prompt_tags': prompt_tags
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
