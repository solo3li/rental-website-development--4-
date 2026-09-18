from django.contrib import admin
from .models import RoommatePost

@admin.register(RoommatePost)
class RoommatePostAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'gender', 'university', 'faculty', 'target_area', 'budget_max_egp', 'is_active', 'created_at')
    list_filter = ('gender', 'university', 'is_active', 'smoking')
    search_fields = ('student_name', 'faculty', 'target_area', 'bio')
