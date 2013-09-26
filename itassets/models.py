#!/usr/bin/python
# -*- coding: utf-8 -*-

# pylint:disable=W0232,R0903,E1101

import random
import string
import datetime

from django.utils.translation import ugettext as _
from django.db import models
from django.db.models import Sum 


class HardwareGroup(models.Model):
    name = models.CharField(max_length=250)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name', )


class Maker(models.Model):
    name = models.CharField(max_length=250)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name', )


class Person(models.Model):
    name = models.CharField(max_length=250)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name', )


class Location(models.Model):
    name = models.CharField(max_length=250)
    note = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return u'%s' % (self.name, )

    class Meta:
        ordering = ('name', )


class Owner(models.Model):
    name = models.CharField(max_length=250)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name', )


class Hardware(models.Model):
    name = models.CharField(max_length=250)
    location = models.ForeignKey(Location)
    hardware_group = models.ForeignKey(HardwareGroup)
    maker = models.ForeignKey(Maker)
    person = models.ManyToManyField(Person, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    inventory_id = models.CharField(max_length=100, blank=True, null=True)
    hostname = models.CharField(max_length=250, blank=True, null=True)
    owner = models.ForeignKey(Owner, default=1)
 
    def __unicode__(self):
        return u'%s %s' % (self.maker, self.name)

    class Meta:
        verbose_name_plural = _("Hardware")
        ordering = ('maker', 'name', )

    def persons(self):
        return ', '.join([str(p) for p in self.person.all()])
    persons.short_description = "Persons"


class Vendor(models.Model):
    name = models.CharField(max_length=250)
    note = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name', )


class Software(models.Model):
    vendor = models.ForeignKey(Vendor, blank=True, null=True)
    name = models.CharField(max_length=250)
    maker = models.ForeignKey(Maker)
    note = models.TextField(blank=True, null=True)
    inventory_id = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return u'%s %s' % (self.maker, self.name)

    class Meta:
        verbose_name_plural = _("Software")
        ordering = ('maker', 'name', )

    def licenses(self):
        return sum([l.remaining() for l in self.license_set.all()])
    licenses.short_description = "Remaining licenses"


class License(models.Model):
    software = models.ForeignKey(Software)
    expires = models.DateField(default=datetime.date(2100, 1, 1))
    count = models.IntegerField(default=1)
    hardware = models.ManyToManyField(Hardware, blank=True, null=True,
                                      through='License2Hardware')
    person = models.ManyToManyField(Person, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    inventory_id = models.CharField(max_length=100, blank=True, null=True)

    def remaining(self):
        result = License2Hardware.objects.filter(license=self)
        result = result.aggregate(consumed=Sum('consumes'))
        try:
            hardware_count = int(result.get('consumed'))
        except TypeError:
            hardware_count = 0
        return (self.count - hardware_count - self.person.count())

    def __unicode__(self):
        return u'%s (%s remaining, expires %s)' % (self.software.name,
                                                   self.remaining(),
                                                   self.expires)
    class Meta:
        ordering = ('software', )


class License2Hardware(models.Model):
    hardware = models.ForeignKey(Hardware)
    license = models.ForeignKey(License)
    consumes = models.IntegerField(default=1)


class SupportContract(models.Model):
    hardware = models.ForeignKey(Hardware)
    expires = models.DateField(default=datetime.date(2100, 1, 1))
    note = models.TextField(blank=True, null=True)
    inventory_id = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return u'%s (expires %s)' % (self.hardware, self.expires)

    class Meta:
        ordering = ('hardware', )


def new_token():
    return ''.join(random.choice(string.ascii_letters + string.digits) for x in range(32)) 


class ExportToken(models.Model):
    token = models.CharField(max_length=100, default=new_token, editable=False)
    note = models.CharField(max_length=100, blank=True, null=True)
