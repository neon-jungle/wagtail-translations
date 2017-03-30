import uuid

from django import forms
from wagtail.wagtailadmin.widgets import AdminPageChooser


class BaseTranslationKeyChoiceField(forms.ModelChoiceField):
    """
    A form field that gets the translation key of a translatable model.
    Set the queryset to determine which model is being translated.
    """
    translation_key_field = 'translation_key'

    def __init__(self, translation_key_field=None, **kwargs):
        if translation_key_field is not None:
            self.translation_key_field = translation_key_field
        super(BaseTranslationKeyChoiceField, self).__init__(**kwargs)

    def to_python(self, value):
        # Converts a model to its translation key
        value = super(BaseTranslationKeyChoiceField, self).to_python(value)
        if value is None:
            return self.initial()
        return getattr(value, self.translation_key_field)

    def prepare_value(self, value):
        if isinstance(value, uuid.UUID):
            value = self.queryset.filter(**{self.translation_key_field: value}).first()
        return super(BaseTranslationKeyChoiceField, self).prepare_value(value)


class TranslatedPageChoiceField(BaseTranslationKeyChoiceField):
    """
    A form field that selects a TranslatedPage, and gets its translation_key.
    """
    widget = AdminPageChooser

    def __init__(self, widget=None, **kwargs):
        # Imported here to prevent circular imports
        from .models import TranslatedPage

        if widget is None:
            # Imported here to prevent circular imports
            widget = self.widget(target_models=[TranslatedPage])

        super(TranslatedPageChoiceField, self).__init__(
            queryset=TranslatedPage.objects.all(),
            widget=widget,
            **kwargs)
