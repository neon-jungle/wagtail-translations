from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from .models import Language


@modeladmin_register
class LanguageModelAdmin(ModelAdmin):
    model = Language
    menu_icon = 'placeholder'
    add_to_settings_menu = True
