from django.apps import AppConfig
from apps.core.i18n import _bi

class ToursConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tours'
    verbose_name = _bi('حجوزات المعاينة والعربون', 'Tours & Deposit')
