from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('matric_number', 'graduation_year', 'program', 'phone', 'current_place', 'is_verified')}),
    )
    list_display = UserAdmin.list_display + ('matric_number', 'graduation_year', 'program', 'is_verified')
    list_filter = UserAdmin.list_filter + ('is_verified',)
    search_fields = UserAdmin.search_fields + ('matric_number', 'email', 'program')
