#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint:disable=W0232,R0904,E1101,R0201

from django.contrib import admin
from django.db.models import Count
from django.db.models import F
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter

from datetime import date, timedelta
from .models import License, Person, Software, Hardware, Vendor
from .models import SupportContract, Location, HardwareGroup, Maker


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
    list_display = ('software', 'expires', 'count', 'remaining', 'note')
    sort_list = ('software', 'expires', 'count', 'remaining')
    list_filter = (RemainingListFilter, ExpireFilter)


class SupportContractAdmin(admin.ModelAdmin):
    list_display = ('hardware', 'expires', 'note')
    sort_list = ('hardware', 'expires', )
    list_filter = (ExpireFilter, )


class LicenseHardwareInline(admin.TabularInline):
    model = License.hardware.through


class HardwareAdmin(admin.ModelAdmin):
    def full_name(self, obj):
        return u'%s' % (obj, )
    full_name.short_description = 'Name'

    list_display = ('full_name', 'note')
    list_filter = ('maker', 'hardware_group')
    inlines = [LicenseHardwareInline, ]
    filter_horizontal = ('person', )


class SoftwareAdmin(admin.ModelAdmin):
    def full_name(self, obj):
        return u'%s' % (obj, )
    full_name.short_description = 'Name'

    list_display = ('full_name', 'note')
    list_filter = ('maker', )


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


admin.site.register(HardwareGroup)
admin.site.register(Maker)
admin.site.register(Location, LocationAdmin)
admin.site.register(Software, SoftwareAdmin)
admin.site.register(Hardware, HardwareAdmin)
admin.site.register(Vendor, VendorAdmin)
admin.site.register(SupportContract, SupportContractAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(License, LicenseAdmin)
