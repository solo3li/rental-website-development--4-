from django.urls import path
from .views import switch_language

app_name = 'core'

urlpatterns = [
    path('switch-lang/', switch_language, name='switch_lang'),
]
