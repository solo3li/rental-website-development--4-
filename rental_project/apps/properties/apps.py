from django.apps import AppConfig
from apps.core.i18n import _bi

class PropertiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.properties'
    verbose_name = _bi('سكن الطلاب والعقارات', 'Properties & Housing')
