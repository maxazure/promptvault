from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app.extensions import db
from app.models import Prompt, Category, Tag, User 
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from app.utils.auth_decorators import admin_required, get_jwt_identity

admin = Blueprint('admin', __name__)

class CategoryForm(FlaskForm):
    """Form for creating and editing categories."""
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    submit = SubmitField('Save')

class TagForm(FlaskForm):
    """Form for creating and editing tags."""
    name = StringField('Name', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Save')

class PromptForm(FlaskForm):
    """Form for creating and editing prompts."""
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Prompt Content', validators=[DataRequired()])
    description = TextAreaField('Description')
    categories = SelectMultipleField('Categories', coerce=str)
    tags = SelectMultipleField('Tags', coerce=str)
    # 如果需要管理员指定用户ID，应该添加以下字段
    # user_id = SelectField('User', coerce=int)
    submit = SubmitField('Save')

    def validate_categories(self, field):
        # 更新choices以包含新输入的值
        current_choices = dict(field.choices)
        for value in field.data:
            if value not in current_choices:
                field.choices.append((value, value))

    def validate_tags(self, field):
        # 更新choices以包含新输入的值
        current_choices = dict(field.choices)
        for value in field.data:
            if value not in current_choices:
                field.choices.append((value, value))

@admin.route('/')
@admin_required
def index(current_user):
    """Admin dashboard."""
    try:
        prompts_count = Prompt.query.count()
        categories_count = Category.query.count()
        tags_count = Tag.query.count()
        return render_template('admin/index.html', 
                              prompts_count=prompts_count, 
                              categories_count=categories_count,
                              tags_count=tags_count)
    except Exception as e:
        flash('认证失败，请重新登录', 'error')
        return redirect(url_for('auth.login'))

@admin.route('/prompts')
@admin_required
def prompts(current_user):
    """List all prompts."""
    page = request.args.get('page', 1, type=int)
    prompts = Prompt.query.order_by(Prompt.created_at.desc()).paginate(
        page=page, per_page=20)
    return render_template('admin/prompts.html', prompts=prompts)

@admin.route('/prompts/new', methods=['GET', 'POST'])
@admin_required
def create_prompt(current_user):
    """Create a new prompt."""
    form = PromptForm()
    user_id = get_jwt_identity()
    # Populate category and tag choices
    form.categories.choices = [(str(c.id), c.name) for c in Category.query.all()]
    form.tags.choices = [(str(t.id), t.name) for t in Tag.query.all()]
    
    if request.method == 'POST':
        # 检查是否为AJAX请求
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = request.get_json()
            form = PromptForm(data=data, meta={'csrf': False})
            if form.validate():
                # 处理表单数据...
                return jsonify({'success': True, 'message': 'Prompt created successfully!'})
            return jsonify({'success': False, 'errors': form.errors}), 400
        
        # 传统表单处理
        for value in form.categories.data:
            if value not in dict(form.categories.choices):
                form.categories.choices.append((value, value))
        for value in form.tags.data:
            if value not in dict(form.tags.choices):
                form.tags.choices.append((value, value))
    
    if form.validate_on_submit():
        prompt = Prompt(
            title=form.title.data,
            content=form.content.data,
            description=form.description.data,
            user_id=user_id
        )
        
        # 处理分类
        categories = []
        for category_data in form.categories.data:
            try:
                category_id = int(category_data)
                category = Category.query.get(category_id)
                if not category:
                    # 如果ID不存在，创建新分类
                    category = Category(name=category_data, user_id=user_id)
                    db.session.add(category)
            except ValueError:
                # 如果不是ID（新输入的分类名），创建新分类
                category = Category(name=category_data, user_id=user_id)
                db.session.add(category)
            categories.append(category)
        
        # 处理标签
        tags = []
        for tag_data in form.tags.data:
            try:
                tag_id = int(tag_data)
                tag = Tag.query.get(tag_id)
                if not tag:
                    # 如果ID不存在，创建新标签
                    tag = Tag(name=tag_data, user_id=user_id)
                    db.session.add(tag)
            except ValueError:
                # 如果不是ID（新输入的标签名），创建新标签
                tag = Tag(name=tag_data, user_id=user_id)
                db.session.add(tag)
            tags.append(tag)
        
        prompt.categories = categories
        prompt.tags = tags
        
        db.session.add(prompt)
        db.session.commit()
        flash('Prompt created successfully!', 'success')
        return redirect(url_for('admin.prompts'))
    
    return render_template('admin/prompt_form.html', form=form, title='New Prompt')

@admin.route('/prompts/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_prompt(id, current_user):
    """Edit an existing prompt."""
    prompt = Prompt.query.get_or_404(id)
    form = PromptForm(obj=prompt)
    user_id = get_jwt_identity()
    
    # Populate category and tag choices
    form.categories.choices = [(str(c.id), c.name) for c in Category.query.all()]
    form.tags.choices = [(str(t.id), t.name) for t in Tag.query.all()]
    
    if request.method == 'GET':
        # Pre-select existing categories and tags
        form.categories.data = [str(c.id) for c in prompt.categories]
        form.tags.data = [str(t.id) for t in prompt.tags]
    else:
        # 在POST请求时更新choices以包含新输入的值
        for value in form.categories.data:
            if value not in dict(form.categories.choices):
                form.categories.choices.append((value, value))
        for value in form.tags.data:
            if value not in dict(form.tags.choices):
                form.tags.choices.append((value, value))
    
    if form.validate_on_submit():
        prompt.title = form.title.data
        prompt.content = form.content.data
        prompt.description = form.description.data
        
        # 处理分类
        categories = []
        for category_data in form.categories.data:
            try:
                category_id = int(category_data)
                category = Category.query.get(category_id)
                if not category:
                    category = Category(name=category_data, user_id=user_id)
                    db.session.add(category)
            except ValueError:
                category = Category(name=category_data, user_id=user_id)
                db.session.add(category)
            categories.append(category)
        
        # 处理标签
        tags = []
        for tag_data in form.tags.data:
            try:
                tag_id = int(tag_data)
                tag = Tag.query.get(tag_id)
                if not tag:
                    tag = Tag(name=tag_data, user_id=user_id)
                    db.session.add(tag)
            except ValueError:
                tag = Tag(name=tag_data, user_id=user_id)
                db.session.add(tag)
            tags.append(tag)
        
        prompt.categories = categories
        prompt.tags = tags
        
        db.session.commit()
        flash('Prompt updated successfully!', 'success')
        return redirect(url_for('admin.prompts'))
    
    return render_template('admin/prompt_form.html', form=form, title='Edit Prompt')

@admin.route('/prompts/<int:id>/delete', methods=['POST'])
@admin_required
def delete_prompt(id, current_user):
    """Delete a prompt."""
    prompt = Prompt.query.get_or_404(id)
    db.session.delete(prompt)
    db.session.commit()
    flash('Prompt deleted successfully!', 'success')
    return redirect(url_for('admin.prompts'))

@admin.route('/categories')
@admin_required
def categories(current_user):
    """List all categories."""
    categories = Category.query.order_by(Category.name).all()
    return render_template('admin/categories.html', categories=categories)

@admin.route('/categories/new', methods=['GET', 'POST'])
@admin_required
def create_category(current_user):
    """Create a new category."""
    form = CategoryForm()
    user_id = get_jwt_identity()
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            description=form.description.data,
            user_id=user_id
        )
        db.session.add(category)
        db.session.commit()
        flash('Category created successfully!', 'success')
        return redirect(url_for('admin.categories'))
    return render_template('admin/category_form.html', form=form, title='New Category')

@admin.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_category(id, current_user):
    """Edit an existing category."""
    category = Category.query.get_or_404(id)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        try:
            db.session.commit()
            flash('Category updated successfully!', 'success')
            return redirect(url_for('admin.categories'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating category. Name may already exist.', 'error')
    return render_template('admin/category_form.html', form=form, title='Edit Category')

@admin.route('/categories/<int:id>/delete', methods=['POST'])
@admin_required
def delete_category(id, current_user):
    """Delete a category."""
    category = Category.query.get_or_404(id)
    try:
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting category. It may be in use.', 'error')
    return redirect(url_for('admin.categories'))

@admin.route('/tags')
@admin_required
def tags(current_user):
    """List all tags."""
    tags = Tag.query.order_by(Tag.name).all()
    return render_template('admin/tags.html', tags=tags)

@admin.route('/tags/new', methods=['GET', 'POST'])
@admin_required
def create_tag(current_user):
    """Create a new tag."""
    form = TagForm()
    user_id = get_jwt_identity()
    if form.validate_on_submit():
        tag = Tag(
            name=form.name.data,
            user_id=user_id
        )
        db.session.add(tag)
        db.session.commit()
        flash('Tag created successfully!', 'success')
        return redirect(url_for('admin.tags'))
    return render_template('admin/tag_form.html', form=form, title='New Tag')

@admin.route('/tags/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_tag(id, current_user):
    """Edit an existing tag."""
    tag = Tag.query.get_or_404(id)
    form = TagForm(obj=tag)
    if form.validate_on_submit():
        tag.name = form.name.data
        try:
            db.session.commit()
            flash('Tag updated successfully!', 'success')
            return redirect(url_for('admin.tags'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating tag. Name may already exist.', 'error')
    return render_template('admin/tag_form.html', form=form, title='Edit Tag')

@admin.route('/tags/<int:id>/delete', methods=['POST'])
@admin_required
def delete_tag(id, current_user):
    """Delete a tag."""
    tag = Tag.query.get_or_404(id)
    try:
        db.session.delete(tag)
        db.session.commit()
        flash('Tag deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting tag. It may be in use.', 'error')
    return redirect(url_for('admin.tags'))

@admin.route('/users')
@admin_required
def get_users(current_user):
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id, current_user):
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': '用户删除成功'})
