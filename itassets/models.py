#!/usr/bin/python
# -*- coding: utf-8 -*-

# pylint:disable=W0232,R0903,E1101

from django.utils.translation import ugettext as _
from django.db import models


class HardwareGroup(models.Model):
    name = models.CharField(max_length=250)

    def __unicode__(self):
        return self.name


class Maker(models.Model):
    name = models.CharField(max_length=250)

    def __unicode__(self):
        return self.name


class Person(models.Model):
    name = models.CharField(max_length=250)

    def __unicode__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=250)
    note = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return u'%s' % (self.name, )


class Owner(models.Model):
    name = models.CharField(max_length=250)

    def __unicode__(self):
        return self.name


class Hardware(models.Model):
    name = models.CharField(max_length=250)
    location = models.ForeignKey(Location)
    hardware_group = models.ForeignKey(HardwareGroup)
    maker = models.ForeignKey(Maker)
    person = models.ManyToManyField(Person, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    inventory_id = models.CharField(max_length=100, blank=True, null=True)
    hostname = models.CharField(max_length=250, blank=True, null=True)
    owner = models.ForeignKey(Owner)

    def __unicode__(self):
        if self.person.all():
            names = ', '.join([str(p) for p in self.person.all()])
            return u'%s %s (%s, %s)' % (self.maker,
                                        self.name,
                                        names,
                                        self.location)
        return u'%s %s (%s)' % (self.maker, self.name, self.location)

    def full_name(self):
        return u'%s' % (self, )
    full_name.short_description = 'Name'

    class Meta:
        verbose_name_plural = _("Hardware")

    def persons(self):
        return ', '.join([str(p) for p in self.person.all()])
    persons.short_description = "Persons"


class Vendor(models.Model):
    name = models.CharField(max_length=250)
    note = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.name


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

    def licenses(self):
        return sum([l.remaining() for l in self.license_set.all()])
    licenses.short_description = "Remaining licenses"


class License(models.Model):
    software = models.ForeignKey(Software)
    expires = models.DateField()
    count = models.IntegerField(default=1)
    hardware = models.ManyToManyField(Hardware, blank=True, null=True)
    person = models.ManyToManyField(Person, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    inventory_id = models.CharField(max_length=100, blank=True, null=True)

    def remaining(self):
        return (self.count - self.hardware.count() - self.person.count())

    def __unicode__(self):
        remaining = self.count - self.hardware.count() - self.person.count()
        return u'%s (%s remaining, expires %s)' % (self.software.name,
                                                   remaining,
                                                   self.expires)

    class Meta:
        ordering = ('software', )


class SupportContract(models.Model):
    hardware = models.ForeignKey(Hardware)
    expires = models.DateField()
    note = models.TextField(blank=True, null=True)
    inventory_id = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return u'%s (expires %s)' % (self.hardware, self.expires)
