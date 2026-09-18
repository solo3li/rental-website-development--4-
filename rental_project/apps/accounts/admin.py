from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'gender', 'phone', 'university', 'company_name', 'created_at')
    list_filter = ('user_type', 'gender', 'university', 'is_verified')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'phone', 'company_name')
