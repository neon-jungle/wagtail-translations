from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.wagtailadmin.widgets import Button
from wagtail.wagtailcore import hooks

from .models import Language, TranslatedPage


class LanguageModelAdmin(ModelAdmin):
    model = Language
    menu_icon = 'fa-language'
    add_to_settings_menu = True


modeladmin_register(LanguageModelAdmin)


class TranslationListingButton(Button):
    template = 'wagtailtranslations/admin/page_listing_button.html'

    def __init__(self, page, page_perms, is_parent, label=_('Translations'), **kwargs):
        super(TranslationListingButton, self).__init__(
            label=label, url=None, **kwargs)
        self.page = page
        self.page_perms = page_perms
        self.is_parent = is_parent

    def render(self):
        return render_to_string(self.template, {
            'button': self,
            'label': self.label,
            'attrs': self.attrs,
            'classes': self.classes,
            'page': self.page,
        })


@hooks.register('register_page_listing_buttons')
def translation_menu(page, page_perms, is_parent=False):
    if isinstance(page, TranslatedPage):
        if page.get_translations().exclude(id=page.pk).exists():
            yield TranslationListingButton(page, page_perms, is_parent)
