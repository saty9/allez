from django.contrib import admin
from .models import Organisation, OrganisationMembership, Address


class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')


class OrganisationMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'organisation', 'state')


admin.site.register(Organisation, OrganisationAdmin)
admin.site.register(OrganisationMembership, OrganisationMembershipAdmin)
admin.site.register(Address)
