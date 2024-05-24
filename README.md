
# WOLFx Admin Configuration

This repository contains the configuration for the WOLFx Admin interface. Below are the instructions and details to understand and extend the functionality of the admin interface.

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

## Usage

- Place the code in the `admin.py` file of your Django application.
- Adjust the configuration constants as needed.
- Define `admin_meta` in your models to customize the admin interface.

## Example Model Configuration

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

## Note

Make sure to replace `'web'` with your actual app name in the `global_app_name` variable.
