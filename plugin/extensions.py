# -*- coding: utf-8 -*-

import gettext
import os

from plugin.settings import LOCAL, TRANSLATIONS_PATH

# localization with fallback
try:
    translation = gettext.translation(
        "messages",
        TRANSLATIONS_PATH,
        languages=[LOCAL],
        fallback=True
    )
except Exception:
    # If translation fails, use NullTranslations (returns original strings)
    translation = gettext.NullTranslations()

_l = translation.gettext
