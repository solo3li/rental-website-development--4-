from django.apps import AppConfig
from apps.core.i18n import _bi

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    verbose_name = _bi('الحسابات والملفات الشخصية', 'Accounts & User Profiles')
