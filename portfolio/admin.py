from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import SiteSettings, OpenSourceProject


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = [
        (_('Hero'), {
            'fields': ['hero_description', 'skills_chips', 'available_for_work', 'contact_email'],
        }),
        (_('About'), {
            'fields': ['about_html'],
        }),
        (_('Social'), {
            'fields': ['github_url', 'linkedin_url', 'medium_url'],
        }),
        (_('Footer'), {
            'fields': ['footer_tagline', 'established_year'],
        }),
    ]

    def has_add_permission(self, request):
        # Only allow one instance
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(OpenSourceProject)
class OpenSourceProjectAdmin(admin.ModelAdmin):
    list_display  = ['name', 'status', 'order']
    list_editable = ['order', 'status']
