from wagtail.admin.edit_handlers import BaseChooserPanel
from wagtail.admin.widgets import AdminPageChooser
from wagtail.utils.decorators import cached_classmethod

from .models import TranslatedPage


class TranslationKeyChooser(AdminPageChooser):
    pass


class BaseTranslationKeyPanel(BaseChooserPanel):
    object_type_name = "page"

    @classmethod
    def widget_overrides(cls):
        from .models import TranslatedPage
        return {cls.field_name: TranslationKeyChooser(
            target_models=[TranslatedPage],
            can_choose_root=False)}

    @cached_classmethod
    def target_models(cls):
        return [TranslatedPage]


class TranslationKeyPanel(object):
    def __init__(self, field_name):
        self.field_name = field_name

    def bind_to_model(self, model):
        return type(str('_TranslationKeyPanel'), (BaseTranslationKeyPanel,), {
            'model': model,
            'field_name': self.field_name,
        })
