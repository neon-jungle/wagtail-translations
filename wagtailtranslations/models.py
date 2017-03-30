from decimal import Decimal
from operator import itemgetter

from django import forms
from django.conf import settings
from django.db import models
from django.db.models import Case, Value, When
from django.http import Http404
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import activate
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.wagtailadmin.forms import (
    WagtailAdminModelForm, WagtailAdminPageForm)
from wagtail.wagtailcore.models import Page

from .fields import PageTranslationKeyField


def split_accept_header(header):
    """
    Take an Accept header and yield `(accept_type, options)` tuples. For
    example:

    .. code-block:: python

        >>> list(split_accept_header('foo, bar;q=0.8, baz;q=0.4;quux=zuul'))
        [('foo', {}), ('bar', {'q': '0.8'}), ('baz', {'q': '0.4', 'quux': 'zuul'})]
    """
    if not header:
        return  # Bail early on an empty string

    for chunk in header.split(','):
        bits = chunk.split(';')
        accept_type = bits[0].strip()
        args = dict(arg.strip().split('=', 2) for arg in bits[1:] if '=' in arg)
        yield accept_type, args


def parse_accept_header(header):
    """
    Return an iterable of accept types from an accept header, in order from
    most acceptable to least.
    """
    options = []
    for accept_type, args in split_accept_header(header):
        try:
            quality = Decimal(args['q'])
        except KeyError:
            quality = 1
        except ValueError:
            continue
        options.append((accept_type, quality))
    return [i[0] for i in sorted(options, key=itemgetter(1), reverse=True)]


def get_request_language_preference(request):
    """
    Collect language preferences from request.LANGUAGE_CODE, the HTTP
    Accept-Language header, and settings.LANGUAGE_CODE, and return a list of
    languages in preference order.
    """
    all_langs = []
    if hasattr(request, 'LANGUAGE_CODE'):
        all_langs.append(request.LANGUAGE_CODE)
    all_langs.extend(parse_accept_header(request.META.get('HTTP_ACCEPT_LANGUAGE', '')))
    all_langs.append(settings.LANGUAGE_CODE)

    # Remove duplicates while preserving order. The list of languages should be
    # quite short, so the inefficiency of this method should not matter.
    # Famous last words.
    langs = []
    for lang in all_langs:
        if lang not in langs:
            langs.append(lang)
    return langs


def get_default_language():
    """
    Used as the default argument for Page to Language foreign keys
    """
    return Language.objects.default_language().pk


class LanguageQuerySet(models.QuerySet):
    def get_user_languages(self, language_preferences):
        """
        Get the best matching Languages for a list of preferences, in order
        from best to worst. All languages will appear in the queryset.
        """
        # Scores: Matched languages will get a score depending upon their
        # preference - better languages will get a higher score, down to 0 for
        # the 'worst' preferenced language. The default language will get a
        # score or -1 unless it matched as a preference, and all other
        # languages will get a score of -2

        # `When` clauses for all the preferred languages
        clauses = [
            When(code__iexact=language, then=Value(i))
            for i, language in enumerate(reversed(language_preferences))]

        # The default language gets a score of -1
        clauses.append(When(is_default=True, then=Value(-1)))

        return self.annotate(
            score=Case(
                *clauses,
                default=Value(-2),  # Everything else gets -2
                output_field=models.IntegerField(null=True))
        ).order_by('-score', 'order')

    def live_q(self):
        return models.Q(live=True)

    def live(self):
        return self.filter(self.live_q())

    def default_language(self):
        return self.filter(is_default=True).first()


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

    @property
    def name(self):
        lang_dict = dict(settings.LANGUAGES)
        return lang_dict.get(self.code, self.code)

    def __str__(self):
        return self.name


class TranslatedPageAdminForm(WagtailAdminPageForm):
    def __init__(self, *args, **kwargs):
        super(TranslatedPageAdminForm, self).__init__(*args, **kwargs)
        if self.parent_page and any(field.name == 'language' for field in self.parent_page.specific._meta.fields):
            self.initial['language'] = self.parent_page.specific.language


class TranslatedPage(Page):
    # Explicitly defined with a unique name so that clashes are unlikely
    translated_page_ptr = models.OneToOneField(
        Page, parent_link=True, related_name='+', on_delete=models.CASCADE)

    # Pages with identical translation_keys are translations of each other
    # Users can change this through the admin UI by picking an existing page
    # this page is a translation of.
    translation_key = PageTranslationKeyField(
        verbose_name=_("translation group"),
        help_text=_(
            "Select another page this is page is a translation of. "
            "Leave this blank if this page has no other version in another language"))

    # Deleting a language that still has pages is not allowed, as it would
    # either lead to tree corruption, or to pages with a null language.
    language = models.ForeignKey(
        Language, on_delete=models.PROTECT, verbose_name=_("language"),
        default=get_default_language)

    translation_panel = MultiFieldPanel([
        FieldPanel('language'),
        FieldPanel('translation_key'),
    ], heading='Translation')

    settings_panels = Page.settings_panels + [translation_panel]

    base_form_class = TranslatedPageAdminForm

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
        request.LANGUAGE_CODE = self.language.code
        return super(TranslatedPage, self).serve(request, *args, **kwargs)

    def get_translations(self):
        return TranslatedPage.objects\
            .select_related('language')\
            .filter(translation_key=self.translation_key,
                    language__in=Language.objects.live())\
            .order_by('language__order')\
            .specific()


class AbstractTranslationIndexPage(Page):

    def serve(self, request):
        language_preferences = get_request_language_preference(request)
        languages = Language.objects.get_user_languages(language_preferences)

        candidate_pages = TranslatedPage.objects\
            .live().specific()\
            .child_of(self)\
            .filter(language__in=languages)\
            .annotate(language_score=Case(
                *[When(language=language, then=Value(i))
                  for i, language in enumerate(languages)],
                default=Value(None),
                output_field=models.IntegerField(null=True)))\
            .order_by('language_score')

        translation = candidate_pages.first()
        if translation:
            # Redirect to the best translation
            return redirect(translation.url)
        else:
            # No translation was found, not even in the default language! Oh dear.
            raise Http404

    class Meta:
        abstract = True
