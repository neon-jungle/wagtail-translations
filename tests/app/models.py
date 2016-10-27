from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page

from wagtailtranslations.models import (
    AbstractTranslationIndexPage, TranslatedPage)


class TranslationHomePage(AbstractTranslationIndexPage):
    subpage_types = ['ContentPage']


class ContentPage(TranslatedPage, Page):
    body = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]
