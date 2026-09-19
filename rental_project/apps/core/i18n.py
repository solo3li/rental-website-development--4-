from django.utils.translation import get_language
from django.utils.functional import lazy

def get_bilingual_text(ar, en):
    lang = get_language() or 'ar'
    return ar if lang.startswith('ar') else en

_bi = lazy(get_bilingual_text, str)

def is_arabic():
    lang = get_language() or 'ar'
    return lang.startswith('ar')
