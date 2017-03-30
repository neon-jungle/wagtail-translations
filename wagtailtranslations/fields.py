import uuid

from django.db import models
from django.utils.text import capfirst

from .forms import TranslatedPageChoiceField


class BaseTranslationKeyField(models.UUIDField):
    """
    A model field that groups instances that are the same item in different
    languages together with a common key.
    """
    def __init__(self, default=uuid.uuid4,
                 db_index=True, **kwargs):
        super(BaseTranslationKeyField, self).__init__(
            default=default, db_index=db_index, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            # Allow users to clear the chosen item, marking this as a
            # translation of nothing except itself.
            'required': False,
            'label': capfirst(self.verbose_name),
            'help_text': self.help_text,
            'initial': self.default,
        }
        defaults.update(kwargs)

        form_class = defaults.pop('form_class')

        return form_class(**defaults)


class PageTranslationKeyField(BaseTranslationKeyField):
    def formfield(self, **kwargs):
        defaults = {'form_class': TranslatedPageChoiceField}
        defaults.update(kwargs)
        return super(PageTranslationKeyField, self).formfield(**defaults)
