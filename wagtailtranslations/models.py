import uuid

from django import forms
from django.conf import settings
from django.db import models
from django.http import Http404
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import activate
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.wagtailadmin.forms import WagtailAdminModelForm
from wagtail.wagtailcore.models import Page


class LanguageQuerySet(models.QuerySet):
    def get_user_languages(self, request):
        """
        Get the best matching Languages for a request, in order from best to
        worst.  The default language (if there is one) will always appear in
        this list.
        """
        # Implementation left as an exercise to the reader
        return self.all()

    def live_q(self):
        return models.Q(live=True)

    def live(self):
        return self.filter(self.live_q())


class LanguageAdminForm(WagtailAdminModelForm):
    code = forms.ChoiceField(
        label=_("language"),
        choices=settings.LANGUAGES,
        help_text=_("One of the languages defined in LANGUAGES"))


class Language(models.Model):
    code = models.CharField(
        _("language code"), max_length=12)

    is_default = models.BooleanField(
        _("is default language?"), default=False, help_text=_("""
        Visitors with no language preference will see the site in this
        language
        """))

    order = models.IntegerField(
        _("order"), help_text=_("""
        Language choices and translations will be displayed in this order
        """))

    live = models.BooleanField(
        _("live"), default=True,
        help_text=_("Is this language available for visitors to view?"))

    objects = LanguageQuerySet.as_manager()

    base_form_class = LanguageAdminForm

    class Meta:
        ordering = ['order']

    def __str__(self):
        lang_dict = dict(settings.LANGUAGES)
        return lang_dict.get(self.code, self.code)


class TranslatedPage(Page):
    # Explicitly defined with a unique name so that clashes are unlikely
    translated_page_ptr = models.OneToOneField(
        Page, parent_link=True, related_name='+', on_delete=models.CASCADE)

    # Pages with identical translation_keys are translations of each other
    # Users can change this through the admin UI, although the raw UUID
    # value should never be shown.
    translation_key = models.UUIDField(
        db_index=True, default=uuid.uuid4, verbose_name=_("translation group"))

    # Deleting a language that still has pages is not allowed, as it would
    # either lead to tree corruption, or to pages with a null language.
    language = models.ForeignKey(
        Language, on_delete=models.PROTECT, verbose_name=_("language"))

    translation_panel = MultiFieldPanel([
        FieldPanel('language'),
        FieldPanel('translation_key'),
    ], heading='Translation')

    settings_panels = Page.settings_panels + [translation_panel]

    is_creatable = False

    class Meta:
        # This class is *not* abstract, so that the unique_together
        # constraint holds across all page classes. Translations of a page
        # do not have to be of the same page type.

        unique_together = [
            # Only one language allowed per translation group
            # FIXME: Adding this causes an error when saving pages!
            # ('translation_key', 'language'),
        ]

    def serve(self, request, *args, **kwargs):
        activate(self.language.code)
        return super().serve(request, *args, **kwargs)

    def get_translations(self):
        return TranslatedPage.objects\
            .select_related('language')\
            .filter(translation_key=self.translation_key,
                    language__in=Language.objects.live())\
            .order_by('language__order')\
            .specific()


class AbstractTranslationIndexPage(Page):

    def serve(self, request):
        languages = Language.objects.get_user_languages(request)

        candidate_pages = TranslatedPage.objects\
            .live().specific()\
            .child_of(self)

        for language in languages:
            try:
                # Try and get a translation in the users language
                translation = candidate_pages.filter(language=language).get()
                # Redirect them to that page instead
                return redirect(translation.url)
            except TranslatedPage.DoesNotExist:
                continue

        # No translation was found, not even in the default language! Oh dear.
        raise Http404

    class Meta:
        abstract = True
