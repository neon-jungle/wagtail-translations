====================
Wagtail translations
====================

A plugin for Wagtail that provides page translations.

Installing
==========

Install using pip:

.. code-block:: sh

    $ pip install wagtailtranslations

Add it to your ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'wagtailtranslations',
        # ...
    ]



It works with Wagtail 1.7 and upwards.

Quick start
===========

Define a ``TranslationIndex`` model:

.. code-block:: python

    from wagtailtranslations.models import AbstractTranslationIndexPage

    class TranslationHomePage(AbstractTranslationIndexPage):
        subpage_types = ['ContentPage']

Use this as your site root page.
Each language your site supports should exist
as a separate page tree underneath this index page.
The English home page should have a slug "en", for a URL of ``/en/``;
while the French home page should have a slug "fr", for a URL of ``/fr/``.

Define a translated model:

.. code-block:: python

    from wagtail.wagtailadmin.edit_handlers import FieldPanel
    from wagtail.wagtailcore.fields import RichTextField
    from wagtail.wagtailcore.models import Page
    from wagtailtranslations.models import TranslatedPage

    class ContentPage(TranslatedPage, Page):
        body = RichTextField()

        content_panels = Page.content_panels + [
            FieldPanel('body'),
        ]

Enable some languages in the Wagtail admin → Settings → Languages,
for example English and French.

Create a new ``ContentPage`` for English.
On the 'Translations' tab, select English for the language,
and leave the 'Translation of ...' field blank.

Create another new ``ContentPage`` for French.
On the 'Translations' tab, select French for the language,
and select the English page you just created in the 'Translation of ...' field.

Testing
=======

To start a test server, run:

.. code-block:: sh

    $ python3 -m venv venv
    $ source venv/bin/activate
    $ pip install -e .
    $ export DJANGO_SETTINGS_MODULE=tests.settings
    $ django-admin migrate
    $ django-admin createsuperuser
    $ django-admin runserver

To run the automated test suite:

.. code-block:: sh

    # Do not run this from within a virtual environment
    $ pip install --user --upgrade tox pip setuptools
    $ tox
