#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint:disable=W0232,R0904,E1101,R0201

from django.contrib import admin
from django.db.models import Count
from django.db.models import F
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter
from django.http import HttpResponse
from django.core import serializers


from datetime import date, timedelta
from .models import License, Person, Software, Hardware, Vendor, Owner, Maker
from .models import SupportContract, Location, HardwareGroup, ExportToken


class RemainingListFilter(SimpleListFilter):
    title = _('Remaining')
    parameter_name = 'remaining'

    def lookups(self, request, model_admin):
        return (
            ('5', '<= 5'),
            ('10', '<= 10'),
            )

    def queryset(self, request, queryset):
        if self.value() == '5':
            return queryset.annotate(
                used_licenses=Count('hardware')).filter(
                used_licenses__gte=F('count') - 5)
        if self.value() == '10':
            return queryset.annotate(
                used_licenses=Count('hardware')).filter(
                used_licenses__gte=F('count') - 10)
        return queryset


class ExpireFilter(SimpleListFilter):
    title = _('Expiration')
    parameter_name = 'expiration'

    def lookups(self, request, model_admin):
        return (
            ('expired', 'Already expired'),
            ('6weeks', 'Within 6 weeks'),
            )

    def queryset(self, request, queryset):
        if self.value() == 'expired':
            today = date.today().strftime('%Y-%m-%d')
            return queryset.filter(expires__lte=today)
        if self.value() == '6weeks':
            soon = (date.today() + timedelta(42)).strftime('%Y-%m-%d')
            return queryset.filter(expires__lte=soon)
        return queryset


class LicenseAdmin(admin.ModelAdmin):
    filter_horizontal = ('hardware', 'person')
    list_display = ('software', 'expires', 'count', 'remaining', 'note', 'inventory_id')
    list_filter = (RemainingListFilter, ExpireFilter)
    search_fields = ['inventory_id', 'person__name', 'hardware__person__name']


class SupportContractAdmin(admin.ModelAdmin):
    list_display = ('hardware', 'expires', 'note', 'inventory_id')
    list_filter = (ExpireFilter, 'hardware__hardware_group')


class LicenseHardwareInline(admin.TabularInline):
    model = License.hardware.through


def export_as_json(modeladmin, request, queryset):
    response = HttpResponse(content_type="application/json")
    serializers.serialize("json", queryset, stream=response)
    return response


class HardwareAdmin(admin.ModelAdmin):
    def full_name(self, obj):
        return u'%s' % (obj, )
    full_name.short_description = 'Name'
 
    list_display = ('full_name', 'note', 'persons', 'location', 'inventory_id', 'maker', 'hardware_group', 'hostname', 'owner')
    list_filter = ('maker', 'hardware_group', 'owner')
    inlines = [LicenseHardwareInline, ]
    filter_horizontal = ('person', )
    search_fields = ['name', 'person__name', 'maker__name', 'inventory_id', 'note', 'hostname']

    actions = [export_as_json]


class SoftwareAdmin(admin.ModelAdmin):
    def full_name(self, obj):
        return u'%s' % (obj, )
    full_name.short_description = 'Name'

    list_display = ('full_name', 'note', 'licenses', 'inventory_id')
    list_filter = ('maker', )
    search_fields = ['name', 'inventory_id', 'note']


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'note')


class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'note')


class HardwarePersonInline(admin.TabularInline):
    model = Hardware.person.through


class LicensePersonInline(admin.TabularInline):
    model = License.person.through


class PersonAdmin(admin.ModelAdmin):
    inlines = [HardwarePersonInline, LicensePersonInline, ]
    search_fields = ['name']


class OwnerAdmin(admin.ModelAdmin):
    list_display = ('name', )


class ExportTokenAdmin(admin.ModelAdmin):
    list_display = ('token', 'note', )
    fields = ['token', 'note',]
    readonly_fields = ['token', ]


admin.site.register(HardwareGroup)
admin.site.register(Maker)
admin.site.register(Location, LocationAdmin)
admin.site.register(Software, SoftwareAdmin)
admin.site.register(Hardware, HardwareAdmin)
admin.site.register(Vendor, VendorAdmin)
admin.site.register(SupportContract, SupportContractAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(License, LicenseAdmin)
admin.site.register(Owner, OwnerAdmin)
admin.site.register(ExportToken, ExportTokenAdmin)
