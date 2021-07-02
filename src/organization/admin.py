from django.contrib import admin
from django.contrib.admin import ModelAdmin

from organization.models import Organization, OrganizationMemberInvitation


class OrganizationAdmin(ModelAdmin):
    model = Organization
    readonly_fields = ["keycloak_data"]
    list_display = ["__str__", "id"]

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()


admin.site.register(Organization, OrganizationAdmin)
admin.site.register(OrganizationMemberInvitation)
