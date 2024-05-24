from django.contrib import admin
from django.forms.models import modelform_factory

# Imports for Dynamic app registrations
from django.apps            import apps

# Models
from web.models             import *

# Json Widget
# from web.widget                import JsonEditorWidget



# CONFIG CONSTANTS
admin.site.site_header  = 'WOLFx Admin'
exempt                  = [] # modelname in this list will not be registered
global_app_name         = 'web' # Replace '' with your app name


# ADMIN.PY MAIN CODE
class GenericStackedAdmin(admin.StackedInline):
    extra = 1

    # This method ensures the field order is correct for inlines as well
    def get_formset(self, request, obj=None, **kwargs):
        formset             =   super().get_formset(request, obj, **kwargs)
        form                =   formset.form
        custom_order        =   [field for field in form.base_fields if field not in CommonModel._meta.fields]
        custom_order        +=  [field for field in CommonModel._meta.fields if field in form.base_fields]
        form.base_fields    =   {field: form.base_fields[field] for field in custom_order}
        return formset


class GenericAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        self.model = model
        self.inlines = []
        self.actions = []
        self.admin_meta = getattr(model, 'admin_meta', {})

        # Dynamic admin meta from model
        # Specify a static dictionary in model
        try:
            # Admin Meta
            if model.admin_meta:
                for k,v in model.admin_meta.items():
                    self.__setattr__(k,v)
        except:
            pass
        
        # Dynamic Actions from model
        # Specify a key 'actions' in the admin_meta dictionary in model
        try:
            if 'actions' in model.admin_meta:
                for action_name in model.admin_meta['actions']:
                    # Ensure action_name is a string
                    if isinstance(action_name, str):
                        action_function = getattr(model, action_name, None)
                        if callable(action_function):
                            self.add_action(action_function, action_name)
        except Exception as e:
            # Handle or log the exception
            pass
        
        # Register Inlines
        self.register_inlines()  

        super().__init__(model, admin_site)
        
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        # Check if the field is a JSONField
        if isinstance(db_field, models.JSONField) and self.admin_meta:
            # Retrieve the schema configuration for JSON fields
            json_fields_meta = self.model.admin_meta.get('json_fields', {})

            # Retrieve the schema for the specific field, if defined
            json_schema = json_fields_meta.get(db_field.name, {}).get('schema')

            if json_schema:
                # Initialize the custom widget with the specified schema
                kwargs['widget'] = JsonEditorWidget(schema=json_schema)
            else:
                # Else load the django-jsoneditor widget 
                kwargs['widget'] = JSONEditor()

        return super().formfield_for_dbfield(db_field, request, **kwargs)

    # Function to get the fieldsets
    def get_fieldsets(self, request, obj=None):
        if 'fieldsets' in self.admin_meta:
            return self.admin_meta['fieldsets']

        common_fields = []
        if issubclass(self.model, CommonModel):
            common_fields = [field.name for field in CommonModel._meta.fields if field.editable]

        other_fields = [field.name for field in self.model._meta.fields if field.name not in common_fields and field.editable and field.name != 'id']
        m2m_fields = [field.name for field in self.model._meta.many_to_many]
        other_fields += m2m_fields

        fieldsets = [
            (self.model._meta.verbose_name.title(), {
                "classes": ["tab"],
                'fields': other_fields,
            })
        ]

        if common_fields:
            fieldsets.append(
                (_("Meta Data"), {
                    "classes": ["tab"],
                    'fields': common_fields,
                })
            )

        return fieldsets
    
    
    def get_readonly_fields(self, request, obj=None):
        # Get a list of non-editable fields
        readonly_fields = [field.name for field in self.model._meta.fields if (not field.editable or field.name == 'id')]

        return readonly_fields
    
    # Function to add actions to the admin class
    def add_action(self, action_function, action_name):
        def wrapper_action(modeladmin, request, queryset):
            for obj in queryset:
                action_method = getattr(obj, action_name)
                if callable(action_method):
                    action_method(request)

        wrapper_action.__name__ = f'admin_action_{action_name}'  # Change the name
        wrapper_action.short_description = action_name.replace('_', ' ').title()

        if not hasattr(self, 'actions') or not self.actions:
            self.actions = [wrapper_action]
        else:
            # Prevent re-adding the same action
            if wrapper_action not in self.actions:
                self.actions.append(wrapper_action)
        
        self.__dict__[wrapper_action.__name__] = wrapper_action
    
    def register_inlines(self):
        if hasattr(self.model, 'admin_meta') and 'inline' in self.model.admin_meta:
            for inline_info in self.model.admin_meta['inline']:
                for related_model, fk_name in inline_info.items():
                    self.add_inline(related_model, fk_name)

    def add_inline(self, related_model_name, fk_name):
        related_model = apps.get_model(app_label=global_app_name, model_name=related_model_name)  # Replace 'your_app_name'
        inline_class_name = f"{related_model.__name__}Inline"
        
        class_attrs = {
            'model'     : related_model,
            'fk_name'   : fk_name,
            'form'      : modelform_factory(related_model, exclude=[]),
        }

        InlineAdminClass = type(inline_class_name, (GenericStackedAdmin,), class_attrs)
        self.inlines.append(InlineAdminClass)

    # Custom Media so that we can add custom js files
    class Media:
        js = ('https://code.jquery.com/jquery-3.7.0.js', )


app = apps.get_app_config(global_app_name)
for model_name, model in app.models.items():
    # If model_name consists history
    if model_name not in exempt and 'histor' not in model_name.lower():
        # print(model_name + ' '  + str(model))
        admin.site.register(model, GenericAdmin)
    
