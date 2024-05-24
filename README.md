
# WOLFx Admin Configuration

This repository contains the configuration for the WOLFx Admin interface. Below are the instructions and details to understand and extend the functionality of the admin interface.

## Usage

1. **Place the code in the `admin.py` file of your Django application.**
2. **Adjust the configuration constants as needed.**
3. **Define `admin_meta` in your models to customize the admin interface.**

## Example Model Configuration 🛠️

Here's an example of how you can define your models to leverage the dynamic admin interface:

```python
class BlogCategory(CommonModel):
    category    =   models.CharField    (max_length=100, unique=True)
    slug        =   models.SlugField    (max_length=100, unique=True)
    image       =   models.FileField    (blank=True,null=True,upload_to='blog_category/')

    def __str__(self):
        return str(self.category)

class Blog(CommonModel):

    head_default='''<meta name="title" content=" ">
    <meta name="description" content=" ">
    <meta name="keywords" content=" ">
    <meta name="robots" content="index, follow">'''

    title               =   models.CharField        (max_length=200)
    sub_title           =   models.CharField        (max_length=200, blank=True ,null=True)
    thumbnail           =   models.ImageField       (upload_to="blog/")
    category            =   models.ForeignKey       (BlogCategory, null=True, on_delete=models.SET_NULL)
    featured_text       =   HTMLField           (null=True, blank=True)
    text                =   HTMLField           (null=True, blank=True)
    slug                =   models.SlugField        (unique=True)
    readtime            =   models.CharField        (max_length=200,null=True, blank=True)
    tags                =   models.TextField        (null=True, blank=True, default='all')
    head                =   models.TextField        (null=True, blank=True, default=head_default)
    
    order_by            =   models.IntegerField     (default=0)
    
    created_at          =   models.DateTimeField    (auto_now_add=True, blank=True, null=True)
    updated_at          =   models.DateTimeField    (auto_now=True, blank=True, null=True)
    created_by          =   models.CharField        (max_length=300)

    admin_meta =    {
        'list_display'      :   ("__str__","category","created_at","updated_at"),
        'list_editable'     :   ("category",),
        'list_per_page'     :   50,
        'list_filter'       :   ("category",),
        'inline'            :   [
            {'BlogImage': 'blog'}
        ]
    }

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name_plural = "Blog"
        ordering = ['order_by'] #Sort in desc order

class BlogImage(CommonModel):
    blog                =   models.ForeignKey       (Blog, on_delete=models.CASCADE)
    image               =   models.ImageField       (upload_to="blog_images/")
    order_by            =   models.IntegerField     (default=0)

    def __str__(self):
        return str(self.blog)

    class Meta:
        verbose_name_plural = "Blog Image"
        ordering = ['order_by'] #Sort in desc order
```

### Using `admin_meta` Dictionary

You can control the admin interface directly from your `models.py` using the `admin_meta` dictionary. Here are some key attributes you can define:

- **`list_display`**: Specify fields to be displayed in the list view.
- **`list_editable`**: Fields that can be edited directly in the list view.
- **`list_filter`**: Fields to filter the list view.
- **`inline`**: Define inline models to be displayed.

### Example with JSONField Schema

If you have a JSONField in your model, you can customize its form field using a schema:

```python
class MyModel(models.Model):
    name = models.CharField(max_length=255)
    data = models.JSONField()

    admin_meta = {
        'json_fields': {
            'data': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'key': {'type': 'string'},
                        'value': {'type': 'number'}
                    }
                }
            }
        },
        'fieldsets': (
            (None, {
                'fields': ('name', 'data')
            }),
        ),
        'actions': ['custom_action'],
        'inline': [
            {'RelatedModel': 'mymodel'}
        ]
    }

    def custom_action(self, request):
        # Custom action logic
        pass
```

### JSON Editor Widget

The `JsonEditorWidget` class is used to render JSON fields with a user-friendly JSON editor:

```python
class JsonEditorWidget(widgets.Widget):
    template_name = 'json_editor_widget.html'

    def __init__(self, schema, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema = schema

    def render(self, name, value, attrs=None, renderer=None):
        json_value = value if value else '{}'
        return mark_safe(f'''
            <!-- JSON Editor Code -->
            <textarea name="{name}" id="tx_{attrs['id']}" style="display:none;">{json_value}</textarea>
            <div id="editor_{attrs['id']}"></div>
            <script>
                document.addEventListener("DOMContentLoaded", function() {{
                    var editor = new JSONEditor(document.getElementById("editor_{attrs['id']}"), {{
                        schema: {self.schema},
                        startval: {json_value},
                        theme: 'html',
                        iconlib: 'fontawesome5',
                    }});
                    editor.on('change', function() {{
                        document.getElementById("tx_{attrs['id']}").value = JSON.stringify(editor.getValue());
                    }});
                }});
            </script>
        ''')
```

## Note 📌

Make sure to replace `'web'` with your actual app name in the `global_app_name` variable.

## Configuration Constants

- `admin.site.site_header`: Sets the header for the admin site.
- `exempt`: A list of model names that should not be registered with the admin.
- `global_app_name`: The name of the application.

## GenericStackedAdmin Class

This class is used for inline models in the admin interface.

### get_formset

This method ensures the field order is correct for inlines.

## GenericAdmin Class

This class provides a dynamic admin interface for models.

### __init__

- Initializes the admin interface for the model.
- Registers inlines and actions dynamically based on model attributes.

### formfield_for_dbfield

- Customizes the form field for JSONField using a schema if defined in the model's admin_meta.

### get_fieldsets

- Defines fieldsets for the admin interface.
- If fieldsets are defined in admin_meta, those are used.

### get_readonly_fields

- Returns a list of non-editable fields.

### add_action

- Adds an action to the admin interface.

### register_inlines

- Registers inlines for the admin interface.

### add_inline

- Adds an inline model to the admin interface.

## Dynamic App Registrations

The models from the specified application are dynamically registered to the admin interface unless they are in the exempt list or have 'histor' in their name.

## Media

Custom media files can be included using the Media class.

