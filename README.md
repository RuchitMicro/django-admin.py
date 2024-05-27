
# Welcome to the WOLFx Admin Configuration repository! 🚀
WOLFx Admin configuration is created to improve the developer experience by simplifying the process of registering models in the admin site. This powerful tool is designed to automate admin registrations but it does not compromise the features that Django's default admin site provides. You can control the admin interface directly from your `models.py` file using a simple `admin_meta` dictionary. This approach eliminates the need for repetitive tasks associated with traditional model registration and allows for direct control over the admin interface, keeping your configurations closely tied to your model definitions.

## Key Features
1. **Automated Model Registration: Automatically register your models in the Django admin site without the hassle of manually creating admin classes.**
2. **Direct Control from Models: Manage your admin configurations right next to your model definitions using the admin_meta dictionary.**
3. **Maintains Django Admin Features: Retain all the robust features offered by Django's default admin site while enjoying the benefits of simplified management.**

## Usage 
1. **Place the code in the `admin.py` file of your Django application.**
2. **Adjust the configuration constants as needed.**
3. **Define `admin_meta` in your models to customize the admin interface.**

## NOTE: Configuration Constants 📌
- `admin.site.site_header`: Sets the header for the admin site.
- `exempt`: A list of model names that should not be registered with the admin. Note that the model_name should be used and not model itself, to understand better uncomment the `print(model_name + ' '  + str(model))` in the second last line of the code to see what is the actual model_name of your model
- `global_app_name`: The name of the application. This constant determines from which app it needs to pull the models for auto-registration. As every app has its admin.py, this constant's value should be the name of its own app. For example if your app name is `web` and the admin.py belongs to this app then the value of this constant should be `web`

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
You can control the admin interface directly from your `models.py` using the `admin_meta` dictionary. Here are some key attributes you can define but are not limited to:

- **`list_display`**: Specify fields to be displayed in the list view.
- **`list_editable`**: Fields that can be edited directly in the list view.
- **`list_filter`**: Fields to filter the list view.
- **`inline`**: Define inline models to be displayed.

### Example with JSONField Schema
If you have a JSONField in your model, you can customize its form field using a schema, note that this makes use of another [open-source project](https://github.com/json-editor/json-editor) and in this version, it's been muted:

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

### JSON Editor Widget - Note: you have to install this dependency to use it [django-jsoneditor](https://pypi.org/project/django-jsoneditor/)
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

## What is WOLFx?
[WOLFx Digital Agency](https://wolfx.io) is a premier IT development company located in the financial capital of India, Mumbai. We specialize in delivering cutting-edge technology solutions and IT services, catering to businesses across various domains and helping them thrive in a digital landscape. Our services include custom software development, web and mobile application development, IT consulting, IT Outsourcing/Staffing, and Digital transformation.

In addition to our commercial endeavors, WOLFx Digital Agency is deeply committed to the open-source community. We actively contribute to open-source projects, sharing our expertise and innovations with the wider tech community. 

## Contribution
We welcome contributions to improve and expand the capabilities of WOLFx Admin Configuration. Please feel free to submit issues, feature requests, or pull requests.

## License
This project is licensed under the MIT License. See the LICENSE file for details.


