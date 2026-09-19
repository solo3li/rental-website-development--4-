from django.apps import AppConfig
from apps.core.i18n import _bi

class RoommatesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.roommates'
    verbose_name = _bi('إعلانات زملاء السكن', 'Roommate Matching')
