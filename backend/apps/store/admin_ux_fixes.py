"""Importing this module (for its side effect — same pattern as
apps/store/admin_persian_numbers.py, imported from every app's admin.py)
patches Django admin's BaseModelAdmin.media so every ModelAdmin *and*
every inline (both inherit from BaseModelAdmin) automatically loads two
extra JS files on their add/change (and list) pages:

- admin/js/fa_admin_novalidate.js — turns off the browser's own native
  HTML5 validation bubbles, which render in the browser's UI language
  regardless of the page's language, so an English tooltip could show up
  even though every one of Django's own (already Persian) error messages
  is correct. See that file's own docstring for the full reasoning.

- admin/js/fa_admin_file_restore.js — re-selects a seller's already-
  chosen product image(s) after the admin redisplays the same form
  because of an unrelated validation error, instead of silently
  resetting every "choose file" input back to empty. See that file's
  own docstring for the full reasoning.

BaseModelAdmin.media is a @property, not a class attribute, and it's the
one thing every admin add/change/list page already renders into
{% block extrahead %} via `{{ media }}` — patching it here (once, at
import time) is what lets both fixes apply to *every* ModelAdmin in the
project without editing each one individually, exactly matching what
was asked: "هر جایی که پنل ادمین این مشکل را دارد" (wherever in the
admin panel this problem exists).
"""

from django import forms
from django.contrib.admin.options import BaseModelAdmin

_original_media = BaseModelAdmin.media.fget

_EXTRA_JS = ("admin/js/fa_admin_novalidate.js", "admin/js/fa_admin_file_restore.js")


def _media_with_fa_admin_ux_fixes(self):
    return _original_media(self) + forms.Media(js=_EXTRA_JS)


BaseModelAdmin.media = property(_media_with_fa_admin_ux_fixes)
